#!/usr/bin/env python
'''
algorithm.py
1) Read object file containing machine code
2) Execute instructions
3) Apply booth's radix 4 algorithm
'''
import sys
from collections import OrderedDict
from common_booth import *

# Declare global variables
object_file = "booth.obj"
op_keys = opcodes.keys()
funct_keys = functs.keys()
reg_keys = registers.keys()

# Map of registers that are available; its an OrderedDict for pretty print purposes
reg_map = OrderedDict([('s0', 0),('r1', 0),('r2', 0),('r3', 0),('r4', 0),('r5', 0),('r6', 0),('r7', 0)])

# Pretty print registers
def pretty_print_registers():
    print("###########################################################")
    print("Register Table:")
    for k,v in reg_map.items():
        print("{}: {:012b}".format(k,v))

# Execute Booth's algorithm given 3 register values
def booths_radix_4(rs, rt, rd):
    # Calculate bit length of both values
    rs_len = bitLen(rs) 
    rt_len = bitLen(rt)

    # Multiplicand and Multiplier values can only be 6 bits
    # Result is a maximum of 12 bits
    val_bit_len = 6
    reg_max_len = val_bit_len*2

    # Sign extend the values until we get 12/13 bits including pad bit
    # A is the multiplicand; B is the multiplier
    A = zero_extend(rs, rs_len,reg_max_len) + integerToBinary(rs, '{:b}')+"0"
    B = integerToBinary(rt, '{:0'+str(val_bit_len)+'b}') + zero_extend(rt, val_bit_len, reg_max_len+1)
    B2 = integerToBinary(reg_map['r3'], '{:0'+str(val_bit_len)+'b}') + zero_extend(rt, val_bit_len, reg_max_len+1)
    negB = integerToBinary(twosComplement(rt), '{:0'+str(val_bit_len)+'b}') + zero_extend(rt, val_bit_len, reg_max_len+1)
    negB2 = integerToBinary(twosComplement(reg_map['r3']), '{:0'+str(val_bit_len)+'b}') + zero_extend(rt, val_bit_len, reg_max_len+1)

    # Log/Display variables used for Booth's algorithm
    print("Variables:")
    print("A   = %d" % unsigned_to_signed(rs))
    print("B   = %d" % unsigned_to_signed(rt))
    print("A   = %s" % (A[0:val_bit_len]+" "+A[val_bit_len:reg_max_len+1]))
    print("B   = %s" % (B[0:val_bit_len]+" "+B[val_bit_len:reg_max_len+1]))
    print("-B  = %s" % (negB[0:val_bit_len]+" "+negB[val_bit_len:reg_max_len+1]))
    print("2B  = %s" % (B2[0:val_bit_len]+" "+B2[val_bit_len:reg_max_len+1]))
    print("-2B = %s" % (negB2[0:val_bit_len]+" "+negB2[val_bit_len:reg_max_len+1]))
    print("###########################################################\n")

    # Calculate how many shifts are needed until algorithm finishes
    totNumShifts = val_bit_len / 2
    cycle = 1
    while(cycle <= totNumShifts):
        print("Cycle %d:" % cycle)
        pad = A[-3:]
        print("\tThe last 3 bits of A are: %s" % "".join(pad))
        if pad == "001" or pad == "010":
            print("\tA = (A+B)")
            A = int(A,2) + int(B,2)
        elif pad == "011":
            print("\tA = (A+2*B)")
            A = int(A,2) + int(B2,2)
        elif pad == "100":
            print("\tA = (A-2*B)")
            A = int(A,2) + int(negB2,2)
        elif pad == "101" or pad == "110":
            print("\tA = (A-B)")
            A = int(A,2) + int(negB,2)
        else: # pad == 111 || pad == 000
            A = int(A,2)

        A = sign_extend(A, bitLen(A), reg_max_len+1, reg_max_len+1) + integerToBinary(A, '{:b}')
        # Clear carry bit if it exists
        A = A[1:] if bitLen(int(A,2)) > reg_max_len+1 else A
        print("\tA = %s" % A)

        # Keep track of sign for later extension
        A = int(A,2)
        msbSigned = isMSBSigned(A, reg_max_len+1)

        print("\tA = A >> 2")
        A = A >> 2

        if msbSigned:
            A = one_extend(A, bitLen(A), reg_max_len+1) + integerToBinary(A, '{:b}')
        else:
            A = zero_extend(A, bitLen(A), reg_max_len+1) + integerToBinary(A, '{:b}')
        print("\tA = %s\n" % A)
        cycle +=1

    # Remove pad bit and assign A to destination register
    A = A[:-1]
    reg_map[rd] = int(A,2)

    # Log multiplication values
    a = unsigned_to_signed(rs)
    b = unsigned_to_signed(rt)
    p = unsigned_to_signed(int(A,2),reg_max_len)
    print("Product of: %d * %d = %d" % (a, b, p))
    print("The answer is: %s\n" % A)

# R instructions are used when all values used are located in registers
# FORMAT: <opcode, rs, rt, rd, funct>
# NOTE: shift format not being used, shift value is in register
def exec_rtype_instr(rs, rt, rd, funct):
    f = funct_keys[functs.values().index(funct)]
    rs = reg_keys[registers.values().index(rs)]
    rt = reg_keys[registers.values().index(rt)]
    rd = reg_keys[registers.values().index(rd)]
    if f == 'bth':
        booths_radix_4(reg_map[rs],reg_map[rt],rd)
    elif f == 'sll':
        reg_map[rd] = reg_map[rs] << reg_map[rt]

# I instructions are used when operating on immediate values
# and a register value
# FORMAT: <opcode, rs, rt, immed>
def exec_immed_instr(opcode, rs, rt, immed):
    op = op_keys[opcodes.values().index(opcode)]
    rs = reg_keys[registers.values().index(rs)]
    rt = reg_keys[registers.values().index(rt)]
    if op == 'lui':
        reg_map[rt] = immed
    elif op == 'ori':
        reg_map[rt] = reg_map[rt] | immed

# For each line in the binary file execute the appropriate instruction
# by parsing the binary
# NOTE: rtype instructions have opcode 0
# Another way to parse is using given bit lengths for each code type
# opcode: 4-bit; registers: 3-bit; function codes: 3-bit; immediate values: 6-bits
def execute_instructions(objectFile):
    for line in objectFile:
        opcode = int(line[0:4],2)
        rs = int(line[4:7], 2)
        rt = int(line[7:10], 2)
        if opcode == 0:     # rtype instruction
            rd = int(line[10:13],2)
            funct = int(line[13:16],2)
            exec_rtype_instr(rs, rt, rd, funct)
        else:               # itype instruction
            immed = int(line[10:16],2)
            exec_immed_instr(opcode, rs, rt, immed)


# MAIN
if __name__ == "__main__":
    print("Processing Machine Code...Computing instructions...\n")

    # Open object binary file
    try:
        infile = open(object_file, 'r')
    except IOError,e:
        print ("Unable to open object file %s" % object_file)
        sys.exit(1)

    # Execute machine instructions from binary file
    execute_instructions(infile)
    infile.close()

    # Print out values in registers
    pretty_print_registers()

    sys.exit(0)
