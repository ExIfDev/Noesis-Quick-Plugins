# Written by aeaxdev 18/10/2025 - 26/09/2026

from inc_noesis import *
import noesis, rapi  # type: ignore
import struct, os

def registerNoesisTypes():
    hMdl = noesis.register("SuperGH model", ".vu0")
    noesis.setHandlerTypeCheck(hMdl, ChkMdl)
    noesis.setHandlerLoadModel(hMdl, LoadMdl)
    return 1

def ChkMdl(data):
    if len(data) < 4:
        return 0
    bs = NoeBitStream(data)
    magic = bs.readBytes(3)
    return 1 if magic == b"VU0" else 0 

def LoadMdl(data, mdl_list):
    bs = NoeBitStream(data)
    rapi.rpgCreateContext()
    
    noesis.logPopup()
    
    iBuf = bytearray()
    vBuf = bytearray()
    nBuf = bytearray()
    uvBuf = bytearray()
    
    bs.readBytes(4)#VU0/n
    ALLOC_SIZE = bs.readUInt()
    unk1 = bs.readUInt()#nr
    unk2 = bs.readUInt()#nr
    unk3 = bs.readUInt()#flags
    MORPH_OFS = bs.readUInt()
    unk5 = bs.readUInt()#u
    unk6 = bs.readUInt()#uc
    BUF_NUM = bs.readUInt()
    VERTEX_COUNT = bs.readUInt()
    MORPH_GRP_CNT = bs.readUInt()
    DECL_OFFS = bs.readUInt()
    unk8 = bs.readUInt()
    unk9 = bs.readUInt()
    
    GIF_OFFS = bs.readUInt()
    VTX_REMAP_OFS = bs.readUInt()
    VB_OFFS = bs.readUInt()
    NB_OFFS = bs.readUInt()
    UVB_OFFS = bs.readUInt()
    UNKB_OFFS = bs.readUInt() #maybe vertex color
    META_OFFS = bs.readUInt()
    META_IDX_OFFS = bs.readUInt()
    AABB_OFFS = bs.readUInt()

    unk10 = bs.readUInt()#uc
    unk14 = bs.readUInt()
    bs.readBytes(0x2c)
    
    print(bs.tell())
    
    print("VERT_CNT:",VERTEX_COUNT)
    print("PACKET_CNT:",BUF_NUM)
    print("VB_OFFS:",VB_OFFS)
    print("NB_OFFS:",NB_OFFS)
    print("UVB_OFFS:",UVB_OFFS)
    print("GIF_OFFS:",GIF_OFFS)
    print("IDX_OFFS:",VTX_REMAP_OFS)
    
    
    bs.seek(MORPH_OFS,NOESEEK_ABS)
    
    
    #VERTEX BUF
    bs.seek(VB_OFFS, NOESEEK_ABS)
    for _ in range(VERTEX_COUNT):
        vBuf.extend(bs.readBytes(12))
        bs.seek(4,NOESEEK_REL)#PAD
        
    #NORMAL BUF
    bs.seek(NB_OFFS, NOESEEK_ABS)
    for _ in range(VERTEX_COUNT):
        nBuf.extend(bs.readBytes(12))
        bs.seek(4,NOESEEK_REL)#PAD
        
    #UV BUF
    bs.seek(UVB_OFFS, NOESEEK_ABS)
    for _ in range(VERTEX_COUNT):
        uvBuf.extend(bs.readBytes(8))
        bs.seek(8,NOESEEK_REL)#PAD
    
    
    rapi.rpgClearBufferBinds()
    rapi.rpgSetName("null")
    
    rapi.rpgBindPositionBuffer(vBuf, noesis.RPGEODATA_FLOAT, 12)
    rapi.rpgBindNormalBuffer(nBuf, noesis.RPGEODATA_FLOAT, 12)
    rapi.rpgBindUV1Buffer(uvBuf, noesis.RPGEODATA_FLOAT, 8)
    
    
    #GIF TAGS https://ps2dev.github.io/ps2sdk/gif__tags_8h_source.html
    tblPos = VTX_REMAP_OFS
    
    for p in range(BUF_NUM):
        
        bs.seek(GIF_OFFS + p * 16,NOESEEK_ABS)
        
        tag0 = bs.readUInt64()
        tag1 = bs.readUInt64()
        
        NLOOP = tag0 & 0x7FFF
        PRIM = (tag0 >> 47) & 0x7FF
        PRIM_TYPE = PRIM & 7
        
        print("PACKET:",p,
              "NLOOP:",NLOOP,
              "PRIM:",hex(PRIM),
              "TYPE:",PRIM_TYPE)
        
        iBuf = bytearray()
        
        bs.seek(tblPos,NOESEEK_ABS)
        
        for _ in range(NLOOP):
            idxOffs = bs.readUInt()
            idx = idxOffs // 16
            
            iBuf.extend(struct.pack("<I",idx))
        
        tblPos += NLOOP * 4
        if PRIM_TYPE == 3: #TRI
            rapi.rpgCommitTriangles(
                iBuf,
                noesis.RPGEODATA_UINT,
                NLOOP,
                noesis.RPGEO_TRIANGLE
            )
        
        
        
        elif PRIM_TYPE == 4:#TRI STRIP
            rapi.rpgCommitTriangles(
                iBuf,
                noesis.RPGEODATA_UINT,
                NLOOP,
                noesis.RPGEO_TRIANGLE_STRIP
            )
        
        
        else:
            print("UNKNOWN PRIM TYPE:",PRIM_TYPE)
    
    rapi.processCommands("-rotate 180 0 0")
    #mdl = NoeModel() 
    mdl = rapi.rpgConstructModel()
    mdl_list.append(mdl)
    return 1