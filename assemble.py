import argparse
import os
from pathlib import Path

from assembler.custom_assembler import CustomAssembler
from assembler.exceptions import AssemblerError, AssemblerException

from bitstring import Bits

from assembler.utils import print_exception

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
        executable_data: Bits = assembler.assemble_file(args.input)
    except AssemblerError as e:
        print_exception(e)
        exit(-1)

    output_filepath = args.output if args.output else Path(args.input).stem + '.o'

    # wb = write binary
    with open(output_filepath, 'wb') as executable:
        executable.write(executable_data.bytes)