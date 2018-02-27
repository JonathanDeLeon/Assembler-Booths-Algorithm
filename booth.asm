# This file contains the custom assembly code that is to be assembled by
# assembly.py for a custom instruction set. The object file output containing
# the machine code 'booth.obj' would theoretically be passed to the Spartan Xilinx
# FPGA board with our custom VHDL code to implement the instructions on the hardware 
# Comments begin with '#'
########################
# Registers Configuration
# $s0 = always null DO NOT USE
# $r1 = A
# $r2 = B
# $r3 = 2B
# $r4 = result 
# $r5 = $temp0
# $r6 = $temp1
# $r7 = 1 (shift register)
# Notes: 
# Highest 6-bit unsigned number = 63 base 10 = 0x3f base 16 = 111 111 base 2
# Highest 6-bit signed number = 31 base 10 = 0x1f base 16 = 011 111 base 2
# Lowest 6-bit signed number = -32 base 10 = 0x20 base 16 = 100 000 base 2
# breaks on 31 * 26
#######################

li $r1, 0x04                # multiplicand into r1
li $r2, 0x05                # multiplier into r2 
li $r7, 0x01                # sets shift register
sll $r3, $r2, $r7           # r3 = r2 << 1
bth $r4, $r1, $r2           # booth's algorithm: r4 = r1 * r2
