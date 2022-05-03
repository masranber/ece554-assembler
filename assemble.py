import argparse
import os
from pathlib import Path

from assembler.custom_assembler import CustomAssembler
from assembler.exceptions import AssemblerError, AssemblerException

from bitstring import Bits

from assembler.utils import print_exception, print_info

# FIBS-J2
# MMAABC
# MACBAM
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input', help='absolute or relative filepath to the assembly file to be assembled')
    parser.add_argument('-o', '--output', help='absolute or relative filepath to write the executable')
    parser.add_argument('-f', '--format', default='binary', choices=['binary','text'], type=str.lower, help='output file format')
    args = parser.parse_args()

    isBinaryFormat: bool = args.format == 'binary'

    assembler = CustomAssembler()
    try:
        executable_data: Bits = assembler.assemble_file(args.input)
    except AssemblerError as e:
        print_exception(e)
        exit(-1)

    output_filepath = args.output if args.output else Path(args.input).stem + ('.o' if isBinaryFormat else '.txt')

    # wb = write binary
    if isBinaryFormat:
        with open(output_filepath, 'wb') as executable:
            for instr in executable_data:
                executable.write(instr.bytes)
    else:
        with open(output_filepath, 'w') as executable:
            for instr in executable_data:
                executable.write(instr.bin + '\n')

    print('SUCCESS: Assembled program written to {} ({})'.format(output_filepath, args.format))