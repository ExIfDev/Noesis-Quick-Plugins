#Written by Aexadev on 28/12/2025
from inc_noesis import *
import noesis, rapi # type: ignore
import struct, math

def registerNoesisTypes():
    harc = noesis.register("There.com asset pack", ".tpq")
    noesis.setHandlerTypeCheck(harc, ChkArc)
    noesis.setHandlerExtractArc(harc, LoadPack)
    
    

    return 1


def ChkArc(data):
    bs  = NoeBitStream(data)
    val = bs.readUInt()
    return 1 if val == 3203334145 else 0

def ChkMdl(data):
    bs  = NoeBitStream(data)
    val = bs.readBytes(4)
    return 1 if val == b"SOM " else 0


def LoadPack(fileName, fileLen, justChecking):
    data = rapi.loadIntoByteArray(fileName)
    bs  = NoeBitStream(data, NOE_LITTLEENDIAN)
    noesis.logPopup()
    
    magic = bs.readUInt()
    if magic != 3203334145:
        return 0
    
    if justChecking:
        return 1
    
    HEAD_SIZE = bs.readUInt()#292
    TOC_OFF = bs.readUInt()#292
    TOC_SIZE = bs.readUInt()
    DATA_OFF = bs.readUInt()
    DATA_SIZ = bs.readUInt()
    unk = bs.readUInt()
    
    FILE_COUNT = TOC_SIZE//284
    

    bs.seek(DATA_OFF,NOESEEK_ABS)
    bf = NoeBitStream(bs.readBytes(DATA_SIZ))
    
    
    
    bs.seek(TOC_OFF,NOESEEK_ABS)
    

    for _ in range(FILE_COUNT):
        FNAME = bs.readString()
        bs.seek(284-len(FNAME)-1-20,NOESEEK_REL)#NULL
        OFFSET = bs.readInt()
        SIZE = bs.readInt()
        unf3 = bs.readUInt()#hash?
        unf4 = bs.readInt()#0
        unf5 = bs.readInt()#0
        print(FNAME, OFFSET, SIZE,hex(unf3),unf4,unf5)
        
        bf.seek(OFFSET,NOESEEK_ABS)
        fdata = bf.readBytes(SIZE)
        rapi.exportArchiveFile(FNAME, fdata)

    return 1




    
        
    
    

    return 1

