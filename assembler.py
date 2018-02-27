#!/usr/bin/env python
'''
assembler.py
'''
import sys
import re
from common_booth import *

# global vars
input_file = "bin/booth.asm"
output_file = "bin/booth.obj"
instructions = []
op_shift = total_bit_length - op_bit_length
rs_shift = op_shift - r_bit_length
rt_shift = rs_shift - r_bit_length
rd_shift = rt_shift - r_bit_length
MAX_IMMED_VALUE = (2**immed_bit_length - 1)

# Some regex notation:
# '^' matches the start of the string
# '$' matches the end of the string
# '(?P<name>...)' the matched part is accessible by the symbolic group name 'name' such as re.group('name') 
# 'A|B' match either A or B
# \s matches whitespace
# '\$' matches '$' character literally
# '[ ]' matches set of characters [0-9A-Fa-f] matches any hex digit 
# re.compile(pattern) compiles a regex pattern into a regex object
f = '|'.join(functs.keys())     # string of all r-type functs for regex
comments    = re.compile(r'''(?P<comment>#.*)$''')
rtype_re    = re.compile(r'''^(?P<instr>('''+f+'''))\s+(?P<rd>\$r[0-7])\s+(?P<rs>\$r[0-7])\s+(?P<rt>\$r[0-7])$''')
dtype_re    = re.compile(r'''^(?P<instr>(lw|sw))\s+(?P<rt>\$r[0-7])\s+(?P<immed>-?(0x)?[0-9a-fA-F]+)$''')
li_re       = re.compile(r'''^(?P<instr>(li))\s+(?P<rt>\$r[0-7])\s+(?P<immed>-?(0x)?[0-9a-fA-F]+)$''')

# Custom Exception if anything goes wrong in the assembler process
class AssemblerError(Exception):
    def __init__(self, line, reason):
        self.line = line
        self.reason = reason
    def __str__(self):
        return "Error on line %d: %s" % (self.line, self.reason)


# 2's complement ranges from -(2^(n-1)) to 2^(n-1)-1
# in this case, immediate values are 6 bits so n = 6
def check_max_signed_value(value, lineNo):
    if value > (2**(immed_bit_length-1) - 1) or value < -(2**(immed_bit_length-1)):
        raise AssemblerError(lineNo,"signed value "+str(value)+" out of range")

def check_max_unsigned_value(value, lineNo):
    if value > (MAX_IMMED_VALUE) or value < 0:
        raise AssemblerError(lineNo,"unsigned value "+str(value)+" out of range")

# if signed bit is set, return same bits without negation in unsigned form
def unsigned_int(value):
    if(value & (1 << (immed_bit_length-1))) != 0:          # checks for signed bit
        value = value & MAX_IMMED_VALUE                    # '&' means bitwise AND both values
    return value

# Assemble instructions based on a given assembly file
def assemble_instructions(inputFile):
    instructions = []
    lineNo = 1
    for line in inputFile:
        # Go to the next line if current line is a comment
        if line[0] == "#":
            lineNo+=1
            continue

        # Remove in-line comments
        line = re.sub(comments, '', line)

        # replace ',' with whitespace and strip beginning and ending whitespaces if any
        instruction = line.replace(',', '').strip()

        if len(instruction) != 0:
            print(instruction)
            # if instruction is not matched, it returns None, otherwise it returns the MatchObject
            rtype = rtype_re.match(instruction)
            dtype = dtype_re.match(instruction)
            li = li_re.match(instruction)
            # convert assembly to proper instructions by type
            if rtype:
                opcode = 0
                rd = registers[rtype.group('rd')[1:]]
                rs = registers[rtype.group('rs')[1:]]
                rt = registers[rtype.group('rt')[1:]]
                funct = functs[rtype.group('instr')] 
                instr = opcode << op_shift | rs << rs_shift | rt << rt_shift | rd << rd_shift | funct
                #print "Instruction is rtype:", rtype.groupdict()
            elif dtype:
                opcode = opcodes[dtype.group('instr')]
                rt = registers[dtype.group('rt')[1:]]
                immed =  int(dtype.group('immed'), 0)       # Converts address or number to an integer in whatever base it is in, hence the '0'
                check_max_signed_value(immed, lineNo)       # Checks if immediate value is too large     
                immed = unsigned_int(immed)                 # apply two's complement if value is negative
                instr = opcode << op_shift | rt << rt_shift | immed 
            elif li:        #This instruction has pseudocode of lui and ori
                rt = registers[li.group('rt')[1:]]
                immed =  int(li.group('immed'), 0)          # Converts address or number to an integer in whatever base it is in, hence the '0'
                check_max_unsigned_value(immed, lineNo)     # Checks if immediate value is too large     
                immed = unsigned_int(immed)                 # apply two's complement if value is negative
                high = (immed >> 6) & MAX_IMMED_VALUE       # get upper 6 bits
                lo = immed & MAX_IMMED_VALUE                # get lower 6 bits
                opcode = opcodes['lui']
                num1 = opcode << op_shift | 0 << rs_shift | rt << rt_shift | high 
                instructions.append(num1)
                opcode = opcodes['ori']
                instr = opcode << op_shift | rt << rs_shift | rt << rt_shift | lo 
            else:
                raise AssemblerError(lineNo,"Can't parse instruction '%s'" % instruction)
            instructions.append(instr)

        lineNo+=1
    return instructions

# Output instruction list of integers to binary
def output_to_binary(instrctions, outFile):
    for instruction in instructions:
        # formats instruction integer to 16-bit binary with leading zeros if necessary
        #print >> outFile, ('{:016b}'.format(instruction))
        outFile.write('{:016b}\n'.format(instruction))

if __name__ == "__main__":
    # Open assembly file
    print("###########################################################")
    print("Starting Assembler\n")

    # Read assembly file
    try:
        infile = open(input_file)
    except IOError,e:
        print ("Unable to open input file %s" % input_file)
        sys.exit(1)

    # Assemble instructions from assembly file
    try:
        infile.seek(0)      #go to the 0 byte in the file
        instructions = assemble_instructions(infile)
        infile.close()
    except AssemblerError, e:
        print(str(e))
        sys.exit(1)

    # Output instructions to binary file
    try:
        outfile = open(output_file, 'w')
        output_to_binary(instructions, outfile)
        outfile.close()
    except IOError,e:
        print ("Unable to open output file %s" % output_file)
        sys.exit(1)

    print("\nAssembler Finished")
    print("###########################################################\n")
    sys.exit(0)
