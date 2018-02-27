'''
Common_booth.py
Commons global variables and methods 
used in both algorithm and assembler
'''
total_bit_length = 16
op_bit_length = 4
r_bit_length = 3
funct_bit_length = 3 
immed_bit_length = 6
# opcodes are 4-bits
# rtype opcode defaults to 0
opcodes = {
    'lw' : 1,
    'sw' : 2,
    'li' : 3,
    'lui' : 4,
    'ori' : 5,
    'andi' : 6,
    'addi' : 7,
}
# functs are 3-bits
functs = {
    'add': 0,
    'sub': 1,
    'bth': 2,
    'sll': 3,
    'srl': 4,
    'mult': 5,
}
# registers are 3-bits
registers = {
    "s0" : 0,
    "r1" : 1,
    "r2" : 2,
    "r3" : 3,
    "r4" : 4,
    "r5" : 5,
    "r6" : 6,
    "r7" : 7
}

#################################################
#common methods used in assembler and algorithm #
#################################################

# Converts unsigned integers to signed integers
def unsigned_to_signed(value, bit_length = immed_bit_length):
    unsigned = value % 2**bit_length 
    signed = unsigned - 2**bit_length if unsigned >= 2**(bit_length-1) else unsigned
    return signed

# apply twos complement to any value 
def twos_complement(value):
    return (2**immed_bit_length) - value

# displays integer in 16 bit binary form
def integer_to_binary(i, form):
    return form.format(i)

# counts actual bit length of a python integer
def bit_len(int_type):
    length = 0
    while (int_type):
        int_type >>= 1
        length += 1
    return(length)

# checks if most significant bit is signed
def is_MSB_signed(value, bit_len):
    return True if(value & (1 << (bit_len-1))) != 0 else False

# Returns the signed extended max_len - bit_len times 
def sign_extend(value, bit_len, s_len, max_len):
    sign_bit = value & 1 << (s_len - 1)
    sign_bit = 1 if sign_bit != 0 else 0
    return "".join([str(sign_bit)] * (max_len-bit_len))

# Returns zero extended max_len - bit_len times 
def zero_extend(value, bit_len, max_len):
    return "".join([str(0)] * (max_len-bit_len))
def one_extend(value, bit_len, max_len):
    return "".join([str(1)] * (max_len-bit_len)) 
