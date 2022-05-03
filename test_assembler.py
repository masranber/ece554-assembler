from typing import List

from assembler.custom_assembler import CustomAssembler
from assembler.exceptions import AssemblerError

from bitstring import Bits

from assembler.utils import print_exception

VALID_INSTRUCTIONS = {
    'HALT'               :Bits(bin='00000 00000000000'),
    'NOP'                :Bits(bin='00001 00000000000'),
    'ADDI $0, $1, #0x0F' :Bits(bin='01000 001 000 01111'),
    'SUBI $1, $2, #-2'   :Bits(bin='01001 010 001 11110'),
    'ST   $2, $3, #0'    :Bits(bin='10000 011 010 00000'),
    'LD   $3, $4, #2'    :Bits(bin='10001 100 011 00010'),
    'VDOT $4, $5, #0x1'  :Bits(bin='00011 101 100 10000'),
    'VDOT $4, $5, #0'    :Bits(bin='00011 101 100 00000'),
    'VLD  $5, $6, #0'    :Bits(bin='00010 110 101 00000'),
    'STU  $6, $7, #0'    :Bits(bin='10011 111 110 00000'),
    'ADD  $7, $6, $5'    :Bits(bin='11001 110 101 111 00'),
    'SUB  $7, $6, $5'    :Bits(bin='11001 110 101 111 01'),
    'SEQ  $0, $1, $2'    :Bits(bin='11100 001 010 000 00'),
    'SLT  $0, $1, $2'    :Bits(bin='11101 001 010 000 00'),
    'SLE  $0, $1, $2'    :Bits(bin='11110 001 010 000 00'),
    'SCO  $0, $1, $2'    :Bits(bin='11111 001 010 000 00'),
    'BEQZ $0, #0xAA'     :Bits(bin='01100 000 101 01010'),
    'BLTZ $0, #-10'      :Bits(bin='01110 000 111 10110'),
    'BGEZ $0, #0x38'     :Bits(bin='01111 000 00111000'),
    'LBI  $0, #22'       :Bits(bin='11000 000 00010110'),
    'SLBI $5, #22'       :Bits(bin='10010 101 00010110'),
    'J #-1024'           :Bits(bin='00100 10000000000'),
    'J #1023'            :Bits(bin='00100 01111111111'),
    'J #0'               :Bits(bin='00100 00000000000'),
    'JR   $4, #0xFF'     :Bits(bin='00101 100 11111111'),
    'JALR $2, #0x81'     :Bits(bin='00111 010 10000001'),
}

LINE_COMMENTS = """
; basic line comments
        ; line comment following whitespace
        ; line comment with leading/trailing whitespace     
        ; HALT
; one ; two ; three
NOP ; comment following instruction

    NOP;weird whitespace
NOP ; NOP
; before
HALT
; after

"""

LINE_COMMENTS_EXPECTED = [
    Bits(bin='0000100000000000'),
    Bits(bin='0000100000000000'),
    Bits(bin='0000100000000000'),
    Bits(bin='0000000000000000'),
]

BLOCK_COMMENTS = """
/* single line */

NOP

/* multi
line */

NOP

/* multi
multi
line
*/

NOP

/* single line */ /* and multi
line */

/* instruction inside
NOP
a comment */

/* before */ NOP /* after */

HALT

/* after */

"""

BLOCK_COMMENTS_EXPECTED = [
    Bits(bin='0000100000000000'),
    Bits(bin='0000100000000000'),
    Bits(bin='0000100000000000'),
    Bits(bin='0000100000000000'),
    Bits(bin='0000000000000000'),
]

SAMPLE_FILE = """

.entry 0x0000 ; tells the assembler where the program will be loaded into memory

/* Begin the text (code) memory segment here */
.segment TEXT

LBI $0, #0 ; R0 will be the counter register
LBI $1, #50 ; R1 will be the bound register

/*  for(int i = 0; i < 50; i++) {
        do nothing
    }
*/
FORLOOP_EVAL:
SUB $2, $1, $0
BEQZ $2, FORLOOP_EXIT ; exit the for loop if counter = bound

; loop body start
NOP ; do nothing
; loop body end

ADDI $0, $0, #1 ; increment loop counter
J FORLOOP_EVAL ; evaluate loop condition again

FORLOOP_EXIT:
HALT

"""

SAMPLE_FILE_EXPECTED = [
    Bits(bin='1100000000000000'),
    Bits(bin='1100000100110010'),
    Bits(bin='1100100100001001'),
    Bits(bin='0110001000000010'),
    Bits(bin='0000100000000000'),
    Bits(bin='0100000000000001'),
    Bits(bin='0010011111111010'),
    Bits(bin='0000000000000000'),
]

def run_test(test_name:str, assembler: CustomAssembler, instrs: List[str], expected_outputs: List[Bits]):
    try:
        actual_outputs: Bits = assembler.assemble_lines(instrs, filename='testbench')
    except AssemblerError as e:
        print_exception(e)
        print('FAILED: Exception thrown')
        exit(-1)

    for i, expected_output in enumerate(expected_outputs):
        if actual_outputs[i] != expected_output:
            print('FAILED: Test \'{}\': \'{}\', expected = {}, actual = {}'.format(test_name, instrs[i], expected_output, actual_outputs[i]))
            exit(-1)

    print('PASSED: Test \'{}\''.format(test_name))

if __name__ == '__main__':
    assembler = CustomAssembler()

    # Test 1: Assemble every instruction and operand type
    instrs, expected_outputs = list(VALID_INSTRUCTIONS.keys()), list(VALID_INSTRUCTIONS.values())
    run_test('Valid Instructions', assembler, instrs, expected_outputs)

    # Test 2: Assemble with line comments
    instrs, expected_outputs = LINE_COMMENTS.splitlines(), LINE_COMMENTS_EXPECTED
    run_test('Line Comments', assembler, instrs, expected_outputs)

    # Test 3: Assemble with block comments
    instrs, expected_outputs = BLOCK_COMMENTS.splitlines(), BLOCK_COMMENTS_EXPECTED
    run_test('Block Comments', assembler, instrs, expected_outputs)

    # Test 3: Assemble sample file with block/line comments, labels, and directives
    instrs, expected_outputs = SAMPLE_FILE.splitlines(), SAMPLE_FILE_EXPECTED
    run_test('Sample File', assembler, instrs, expected_outputs)

    print('SUCCESS: All tests passed')