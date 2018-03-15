
.equ ANIM_TABLE_ENTRY_SIZE, 8
.macro anim_table_entry frame_table, tile_num, tile_count, speed, frame_count_mask
.4byte (\frame_table)
.2byte (\tile_num)
.byte (\tile_count)
.byte ((\frame_count_mask) | ((\speed) << 5))
.endm

//.equ INSERTION_OFFSET, 0x8ef0000
//.equ BPEE,1
//.equ PRIMARY,1
.include "resources/rom_offsets.inc"

.thumb
.align 2
prepareTilesetCB:
    ldr r1, =TilesetCBCounter
    mov r0, #0x0
    strh r0, [r1]

    ldr r1, =TilesetCBBufferSize
    mov r0, #0x1
    lsl r0, r0, #0xf//#0x8
    strh r0, [r1]

    ldr r1, =TilesetCB
    ldr r0, =(animationCB + (INSERTION_OFFSET | 1))
    str r0, [r1]
    
    bx lr

.pool


.align 2
animationCB:            // void animationCB(u16 timer)
    push {r4-r6, lr}
    mov r4, r0
    ldr r5, =(AnimHeaderTable + INSERTION_OFFSET)
    ldr r6, =(AnimHeaderTableEnd + INSERTION_OFFSET)

loop:
    ldrb r1, [r5, #0x7]
    lsr r2, r1, #0x5
    add r2, r2, #0x1
    mov r0, #0x1
    lsl r0, r0, r2
    sub r0, r0, #0x1    
    and r0, r0, r4
    
    // If the timer & the animation bit mask == 0, prepare DMA
    cmp r0, #0x0
    bne continue
    
    // Get frame image pointer at r0
    lsl r1, r1, #27
    lsr r1, r1, #27
    mov r0, r4
    lsr r0, r0, r2
    and r0, r0, r1
    ldr r1, [r5]
    lsl r0, r0, #0x2
    add r0, r0, r1
    ldr r0, [r0]
    
    // Get VRAM tile pointer
    ldrh r1, [r5, #0x4]
    lsl r1, r1, #0x5    // a tile is 32 bytes
    mov r2, #0x6
    lsl r2, #0x18
    add r1, r1, r2
    
    // Get size of data
    ldrb r2, [r5, #0x6]
    lsl r2, r2, #0x5
    
    //bl (AppendTilesetAnimToBuffer - INSERTION_OFFSET)
    ldr r3, =(AppendTilesetAnimToBuffer | 1)
    bl bx_r3

continue:
    add r5, r5, #ANIM_TABLE_ENTRY_SIZE
    cmp r5, r6
    blo loop
    pop {r4-r6, pc}

bx_r3:
    bx r3

.pool

.include "tmp_animation_table.inc"
