#!/usr/bin/env python
'''
algorithm.py
'''
import sys
import re
from collections import OrderedDict
from common_booth import *

object_file = "booth.obj"
op_keys = opcodes.keys()
funct_keys = functs.keys()
reg_keys = registers.keys()
r = OrderedDict([('s0', 0),('r1', 0),('r2', 0),('r3', 0),('r4', 0),('r5', 0),('r6', 0),('r7', 0)]) 

def print_registers():
    print("###########################################################")
    print("Register Table:")
    for k,v in r.items():
        print("{}: {:012b}".format(k,r[k]))

def boothsRadix4(rs, rt, rd):
    # Calculate bit length of both values
    rs_len = bitLen(rs) 
    rt_len = bitLen(rt) 
    #big_len = rs_len if rs_len >= rt_len else rt_len        # larger length between the two
    #big_len = big_len if big_len % 2 == 0 else big_len+1     # make sure big_len is multiple of 2
    big_len = 6
    max_len = big_len*2                                     
    # Sign extend the values until we get max_len +1 bits
    A = zero_extend(rs, rs_len,max_len) + integerToBinary(rs, '{:b}')+"0"
    B = integerToBinary(rt, '{:0'+str(big_len)+'b}') + zero_extend(rt, big_len, max_len+1)
    B2 = integerToBinary(r['r3'], '{:0'+str(big_len)+'b}') + zero_extend(rt, big_len, max_len+1)
    negB = integerToBinary(twosComplement(rt), '{:0'+str(big_len)+'b}') + zero_extend(rt, big_len, max_len+1)
    negB2 = integerToBinary(twosComplement(r['r3']), '{:0'+str(big_len)+'b}') + zero_extend(rt, big_len, max_len+1)
    totNumShifts = big_len / 2          # Calculate how many shifts are needed until algorithm finishes
    step = 1
    print("Variables:")
    print("A   = %d" % unsigned_to_signed(rs))
    print("B   = %d" % unsigned_to_signed(rt))
    print("A   = %s" % (A[0:big_len]+" "+A[big_len:max_len+1]))
    print("B   = %s" % (B[0:big_len]+" "+B[big_len:max_len+1]))
    print("-B  = %s" % (negB[0:big_len]+" "+negB[big_len:max_len+1]))
    print("2B  = %s" % (B2[0:big_len]+" "+B2[big_len:max_len+1]))
    print("-2B = %s" % (negB2[0:big_len]+" "+negB2[big_len:max_len+1]))
    print("###########################################################\n")
    while(step <= totNumShifts):
        print("Step %d:" % step)
        pad = A[-3:]
        print("    " + "The last 3 bits of A are: %s" % "".join(pad))
        if pad == "001" or pad == "010":
            print("    " + "A = (A+B)")
            #A = integerToBinary(int(A,2) + int(B,2), '{:b}')
            A = int(A,2) + int(B,2)
            A = sign_extend(A, bitLen(A), max_len+1, max_len+1) + integerToBinary(A, '{:b}')
            print("    " + "A = %s" % A)
        elif pad == "011":
            print("    " + "A = (A+2*B)")
            A = int(A,2) + int(B2,2)
            A = sign_extend(A, bitLen(A), max_len+1, max_len+1) + integerToBinary(A, '{:b}')
            print("    " + "A = %s" % A)
        elif pad == "100":
            print("    " + "A = (A-2*B)")
            A = int(A,2) + int(negB2,2)
            A = sign_extend(A, bitLen(A), max_len+1, max_len+1) + integerToBinary(A, '{:b}')
            print("    " + "A = %s" % A)
        elif pad == "101" or pad == "110":
            print("    " + "A = (A-B)")
            A = int(A,2) + int(negB,2)
            A = sign_extend(A, bitLen(A), max_len+1, max_len+1) + integerToBinary(A, '{:b}')
            print("    " + "A = %s" % A)
        print("    " + "A = A >> 2")
        A = A[1:] if bitLen(int(A,2)) > max_len+1 else A    # Clear carry bit if it exists
        A = int(A,2)
        msbSigned = isMSBSigned(A, max_len+1)
        A = A >> 2
        #A = sign_extend(A, bitLen(A), max_len+1, max_len+1) + integerToBinary(A, '{:b}')
        if msbSigned:
            A = one_extend(A, bitLen(A), max_len+1) + integerToBinary(A, '{:b}')
        else:
            A = zero_extend(A, bitLen(A), max_len+1) + integerToBinary(A, '{:b}')
        print("    " + "A = %s\n" % A)
        step +=1
    A = A[:-1]      # Remove pad bit
    r[rd] = int(A,2)
    a = unsigned_to_signed(rs)
    b = unsigned_to_signed(rt)
    p = unsigned_to_signed(int(A,2),max_len)
    print("Product of: %d * %d = %d" % (a, b, p))
    print("The answer is: %s\n" % A)

def exec_rtype_instr(rs, rt, rd, funct):
    f = funct_keys[functs.values().index(funct)]
    rs = reg_keys[registers.values().index(rs)]
    rt = reg_keys[registers.values().index(rt)]
    rd = reg_keys[registers.values().index(rd)]
    if f == 'bth':
        boothsRadix4(r[rs],r[rt],rd)
    elif f == 'sll':
        r[rd] = r[rs] << r[rt] 

def exec_immed_instr(opcode, rs, rt, immed):
    op = op_keys[opcodes.values().index(opcode)]
    rs = reg_keys[registers.values().index(rs)]
    rt = reg_keys[registers.values().index(rt)]
    if op == 'lui':
        r[rt] = immed
    elif op == 'ori':
        r[rt] = r[rt] | immed

def execute_instructions(objectFile):
    for line in objectFile:
        opcode = int(line[0:op_bit_length],2) 
        rs = int(line[4:7],2)
        rt = int(line[7:10],2)
        if opcode == 0:     # rtype instruction
            rd = int(line[10:13],2)
            funct = int(line[13:16],2)
            exec_rtype_instr(rs, rt, rd, funct)
        else:               # itype instruction
            immed = int(line[10:16],2)
            exec_immed_instr(opcode, rs, rt, immed)

    print_registers()
if __name__ == "__main__":
    print("Processing Machine Code...Computing instructions...\n")
    # Open object binary file
    try:
        infile = open(object_file, 'r')
    except IOError,e:
        #print >> sys.stderr, ("Unable to open object file %s" % object_file)
        print ("Unable to open object file %s" % object_file)
        sys.exit(1)

    # Read object binary file executing the machine instructions 
    instructions = execute_instructions(infile)
    infile.close()

    sys.exit(0)
