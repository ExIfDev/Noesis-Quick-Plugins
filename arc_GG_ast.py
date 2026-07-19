#written by Aexadev on 19/07/2026
from inc_noesis import *
import noesis, rapi # type: ignore

#.ast container, I Spy Spooky Mansion, Gusto Games

def registerNoesisTypes():
    
    harc = noesis.register("GGEngine asset", ".ast")
    noesis.setHandlerTypeCheck(harc, ChkArc)
    noesis.setHandlerExtractArc(harc, LoadRes)
    

    return 1

def ChkArc(data):
    bs  = NoeBitStream(data)
    val = bs.readBytes(8)
    return 1 if val == b"SDASSETF" else 0

def LoadRes(fileName, fileLen, justChecking):
    data = rapi.loadIntoByteArray(fileName)
    bs  = NoeBitStream(data, NOE_BIGENDIAN)
    noesis.logPopup()

    magic = bs.readBytes(8)
    if magic != b"SDASSETF":
        return 0
    
    unk1 = bs.readInt()#version?
    FILE_COUNT = bs.readInt()
    
    if justChecking:
        return 1

    for i in range(FILE_COUNT):
        _ds = bs.tell()
        A_TYPE = bs.readBytes(4)
        
        if A_TYPE == b"BMAP":
            bunk1= bs.readUShort() #128 palette?
            bunk2= bs.readUShort() #maybe bpp?
            unk_size= bs.readUInt() #size of something
            IMAG_SIZE= bs.readUInt() #size of the IMAG chunk
            FNAME= ByteAlignedStr(bs)+".bmap"
            bs.readBytes(unk_size)
            bs.readBytes(IMAG_SIZE)
            
            print("[%d] %s " % (i,FNAME))
            
        else:
            noesis.doException("Unrecognized file header: %s" % str(A_TYPE))
        _de = bs.tell()
        
        
        
        bs.seek(_ds,NOESEEK_ABS)
        _fData = bs.readBytes(_de-_ds)
        rapi.exportArchiveFile(FNAME, _fData)
        bs.seek(_de,NOESEEK_ABS)
    return 1
    
def ByteAlignedStr(bs):
    _start = bs.tell()
    string = bs.readString()
    alignment = -(bs.tell() - _start) % 4
    bs.seek(alignment, NOESEEK_REL)
    return string
    
