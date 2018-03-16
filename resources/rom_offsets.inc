
.ifdef PRIMARY
.equ VRAM_Tile_0, 0x06000000
.endif
.ifdef SECONDARY
    // Redefined in BPRE
.equ VRAM_Tile_0, 0x06004000
.endif


.ifdef BPEE
.equ AppendTilesetAnimToBuffer, 0x080a0980

.ifdef PRIMARY
.equ TilesetCB, 0x03000f40
.equ TilesetCBCounter, 0x03000f36
.equ TilesetCBBufferSize, 0x03000f38
.endif // PRIMARY

.ifdef SECONDARY
.equ TilesetCB, 0x03000f44
.equ TilesetCBCounter, 0x03000f3a
.equ TilesetCBBufferSize, 0x03000f3c
.endif // SECONDARY

.endif // BPEE

.ifdef BPRE
.equ AppendTilesetAnimToBuffer, 0x0806ff04

.ifdef PRIMARY
.equ TilesetCB, 0x03000fb8
.equ TilesetCBCounter, 0x03000fae
.equ TilesetCBBufferSize, 0x03000fb0
.endif // PRIMARY

.ifdef SECONDARY
.equ VRAM_Tile_0, 0x06005000
.equ TilesetCB, 0x03000fbC
.equ TilesetCBCounter, 0x03000fb2
.equ TilesetCBBufferSize, 0x03000fb4
.endif // SECONDARY

.endif // BPRE

.ifdef AXVE
.equ AppendTilesetAnimToBuffer, 0x08072e24

.ifdef PRIMARY
.equ TilesetCB, 0x030006cc
.equ TilesetCBCounter, 0x030006c2
.equ TilesetCBBufferSize, 0x030006c4
.endif // PRIMARY

.ifdef SECONDARY
.equ TilesetCB, 0x030006d0
.equ TilesetCBCounter, 0x030006c6
.equ TilesetCBBufferSize, 0x030006c8
.endif // SECONDARY

.endif // AXVE

