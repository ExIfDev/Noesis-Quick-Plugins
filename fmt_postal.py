#Written by Aexadev on 16/09/2026

#Postal 1

from inc_noesis import *
import noesis, rapi  # type: ignore
import struct, os

def registerNoesisTypes():
    for ext in [".sop", ".mesh"]:
        hMdl = noesis.register("POSTAL model", ext)
        noesis.setHandlerTypeCheck(hMdl, ChkMdl)
        noesis.setHandlerLoadModel(hMdl, LoadMdl)
    
    hsak = noesis.register("POSTAL asset archive", ".sak")
    noesis.setHandlerTypeCheck(hsak, ChkArc)
    noesis.setHandlerExtractArc(hsak, LoadArc)    

    global USE_HOOD
    USE_HOOD = False                                        
    hUhToggle = noesis.registerTool("Use hood", useHoodToggle)
    noesis.setToolSubMenuName(hUhToggle, "POSTAL")
    noesis.checkToolMenuItem(hUhToggle, USE_HOOD)
    return 1

def ChkMdl(data):
    if len(data) < 4:
        return 0
    bs = NoeBitStream(data)
    magic = bs.readBytes(4)
    return 1 if magic == b"CHAN" else 0 


def ChkArc(data):
    if len(data) < 4:
        return 0
    bs = NoeBitStream(data)
    magic = bs.readBytes(4)
    return 1 if magic == b"SAK " else 0 

def useHoodToggle(toolIndex):
    global USE_HOOD
    USE_HOOD = not USE_HOOD
    noesis.checkToolMenuItem(toolIndex, USE_HOOD)
    return 1

def LoadMdl(data, mdl_list):
    rapi.rpgCreateContext()
    noesis.logPopup()

    BASE_FNAME = rapi.getExtensionlessName(rapi.getInputName())

    #MESH
    meshData = rapi.loadIntoByteArray(BASE_FNAME + ".mesh")
    bs = NoeBitStream(meshData)
    #unkdata
    bs.seek(30, NOESEEK_ABS)
    TRI_CNT = bs.readUShort()
    indices = []

    for tri in range(TRI_CNT):
        indices.append(bs.readUShort())
        indices.append(bs.readUShort())
        indices.append(bs.readUShort())

    #SOP SeaOfPoints
    sopData = rapi.loadIntoByteArray(BASE_FNAME + ".sop")
    bs = NoeBitStream(sopData)
    #unkdata
    bs.seek(26, NOESEEK_ABS)
    VERTEX_CNT = bs.readUInt()
    positions = []
    for i in range(VERTEX_CNT):
        x = bs.readFloat()
        y = bs.readFloat()
        z = bs.readFloat()
        positions.append((x, y, z))
        bs.readFloat()


    #TEX
    texData = rapi.loadIntoByteArray(BASE_FNAME + ".tex")
    bs = NoeBitStream(texData)
    #unkdata
    bs.seek(30, NOESEEK_ABS)
    VCOL_CNT = bs.readUShort()
    COL_TYP = bs.readUShort()
    faceColors = []
    if COL_TYP == 1:
        for tri in range(VCOL_CNT):
            faceColors.append(bs.readUByte())
    palette = None
    if USE_HOOD and COL_TYP == 1:
        hoodPltDta = rapi.loadPairedFile("POSTAL hood", ".bmp")
        if hoodPltDta:
            if hoodPltDta[:2] != b"BM":
                noesis.doException("hood file is not a BMP!?")
            else:
                dibSize = struct.unpack_from("<I", hoodPltDta, 14)[0]
                bpp = struct.unpack_from("<H", hoodPltDta, 28)[0]
                palOfs = 14 + dibSize
                palette = []
                for i in range(256):
                    b, g, r, _ = struct.unpack_from(
                        "<BBBB",
                        hoodPltDta,
                        palOfs + (i * 4)
                    )
                    palette.append((r, g, b))

    vBuf = bytearray()
    vcBuf = bytearray()
    iBuf = bytearray()

    iIndex = 0
    for tri in range(TRI_CNT):
        if palette is not None and tri < len(faceColors):
            palIndex = faceColors[tri]
            r, g, b = palette[palIndex]
        else:
            r = 255
            g = 255
            b = 255
        for tc in range(3):

            srcIndex = indices[(tri * 3) + tc]
            x, y, z = positions[srcIndex]
            vBuf.extend(struct.pack("<3f", x, y, z))
            vcBuf.extend(bytes((r, g, b)))
            iBuf.extend(struct.pack("<I", iIndex))
            iIndex += 1
    rapi.rpgClearBufferBinds()

    rapi.rpgSetName(rapi.getExtensionlessName(rapi.getLocalFileName(rapi.getInputName())))
    rapi.rpgBindPositionBuffer(vBuf,noesis.RPGEODATA_FLOAT,12)

    if palette is not None: rapi.rpgBindColorBuffer(vcBuf,noesis.RPGEODATA_UBYTE,3,3)
    rapi.rpgCommitTriangles(iBuf,noesis.RPGEODATA_UINT,iIndex,noesis.RPGEO_TRIANGLE,1)
    mdl = rapi.rpgConstructModel()
    mdl_list.append(mdl)

    return 1


def LoadArc(fileName, fileLen, justChecking):
    data = rapi.loadIntoByteArray(fileName)
    bs  = NoeBitStream(data) 
    vr = bs.readBytes(4)  
    if vr != b"SAK ":
        return 0
    
    noesis.logPopup()
    
    if justChecking:
        return 1  
    
    fNameLst = []
    fOffsLst = []
    VER = bs.readUInt()
    FCNT = bs.readUShort()
    for f in range(FCNT):
        fName = bs.readString()
        fNameLst.append(fName)
        fOfs = bs.readUInt()
        fOffsLst.append(fOfs)
        
    for fl in range(FCNT):
        FNAME = fNameLst[fl]
        FOFF = fOffsLst[fl]

        ascOffs = [ofs for ofs in fOffsLst if ofs > FOFF]
        if ascOffs:
            subsOffs = min(ascOffs)
        else:
            subsOffs = bs.getSize()
        FSIZE = subsOffs - FOFF

        print( "[", fl + 1, "/", FCNT, "]",FNAME,FSIZE,FOFF)

        bs.seek(FOFF, NOESEEK_ABS)
        fData = bs.readBytes(FSIZE)
        rapi.exportArchiveFile(FNAME, fData)

    return 1

