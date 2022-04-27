
.entry 0x0000 ; tells the assembler where the program will be loaded into memory

/* Begin the text (code) memory segment here */
.segment TEXT

LBI $R0, #0 ; R0 will be the counter register
LBI $R1, #50 ; R1 will be the bound register

/*  for(int i = 0; i < 50; i++) {
        do nothing
    }
*/
FORLOOP_EVAL:
SUB $R2, $R1, $R0
BEQZ $R2, FORLOOP_EXIT ; exit the for loop if counter = bound

; loop body start
NOP ; do nothing
; loop body end

ADDI $R0, $R0, #1 ; increment loop counter
J FORLOOP_EVAL ; evaluate loop condition again

FORLOOP_EXIT:
HALT

/* Begin the data (initialized global variables) memory segment here */
.segment DATA
.value ZERO 0x0000 ; initialize a word of memory with the specified value and name
.value SONG_BASE_ADDR 0x0400
.string HELLO_WORLD "Hello world!" ; initialize a string of ASCII characters in memory (implicitly null terminated by assembler, each character gets its own word)
