
.if BPEE
.equ AppendTilesetAnimToBuffer, 0x080a0980

.if PRIMARY
.equ TilesetCB, 0x03000f40
.equ TilesetCBCounter, 0x03000f36
.equ TilesetCBBufferSize, 0x03000f38

.elseif SECONDARY
.equ TilesetCB, 0x03000f44
.equ TilesetCBCounter, 0x03000f3a
.equ TilesetCBBufferSize, 0x03000f3c

.endif

.elseif BPRE
.equ AppendTilesetAnimToBuffer, 0x0806ff04

.if PRIMARY
.equ TilesetCB, 0x03000fb8
.equ TilesetCBCounter, 0x03000fae
.equ TilesetCBBufferSize, 0x03000fb0

.elseif SECONDARY
.equ TilesetCB, 0x03000fbC
.equ TilesetCBCounter, 0x03000fb2
.equ TilesetCBBufferSize, 0x03000fb4

.endif

.elseif AXVE
..equ AppendTilesetAnimToBuffer, 0x08072e24

.if PRIMARY
.equ TilesetCB, 0x030006cc
.equ TilesetCBCounter, 0x030006c2
.equ TilesetCBBufferSize, 0x030006c4

.elseif SECONDARY
.equ TilesetCB, 0x030006d0
.equ TilesetCBCounter, 0x030006c6
.equ TilesetCBBufferSize, 0x030006c8

.endif

.endif
