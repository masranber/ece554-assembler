import argparse
import os
from pathlib import Path

from assembler.custom_assembler import CustomAssembler
from assembler.exceptions import AssemblerError, AssemblerException

from bitstring import Bits

from assembler.utils import print_exception

VALID_INSTRUCTIONS = {
    'HALT'               :Bits(bin='0000000000000000'),
    'NOP'                :Bits(bin='0000100000000000'),
    'ADDI $0, $1, #0x1F' :Bits(bin='0100000000111111'),
    'SUBI $1, $2, #-2'   :Bits(bin='0100100101011110'),
    'ST   $2, $3, #0'    :Bits(bin='1000001001100000'),
    'LD   $3, $4, #2'    :Bits(bin='1000101110000010'),
    'VDOT $4, $5'        :Bits(bin='000111001010000'),
    'VLD  $5, $6, #0'    :Bits(bin='0001010111000000'),
    'STU  $6, $7, #0'    :Bits(bin='1001111011100000'),
    'ADD  $7, $6, $5'    :Bits(bin='1100111111010100'),
    'SUB  $7, $6, $5'    :Bits(bin='1100111111010101'),
    'SEQ  $0, $1, $2'    :Bits(bin='1110000000101000'),
    'SLT  $0, $1, $2'    :Bits(bin='1110100000101000'),
    'SLE  $0, $1, $2'    :Bits(bin='1111000000101000'),
    'SCO  $0, $1, $2'    :Bits(bin='1111100000101000'),
    'BEQZ $0, #0xAA'     :Bits(bin='0110000010101010'),
    'BLTZ $0, #-10'      :Bits(bin='0111000011110110'),
    'BLTZ $0, #-10'      :Bits(bin='0111000011110110'),
}

# FIBS-J2
# MMAABC
# MACBAM
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input', help='absolute or relative filepath to the assembly file to be assembled')
    parser.add_argument('-o', '--output', help='absolute or relative filepath to write the executable')
    args = parser.parse_args()

    assembler = CustomAssembler()
    try:
        assembler.assemble_lines
        executable_data: Bits = assembler.assemble_file(args.input)
    except AssemblerError as e:
        print_exception(e)
        exit(-1)

    output_filepath = args.output if args.output else Path(args.input).stem + '.o'

    # wb = write binary
    with open(output_filepath, 'wb') as executable:
        executable.write(executable_data.bytes)