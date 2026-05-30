#for Easy FPS Editor
#Written by Aexadev 23/11/2025

from inc_noesis import *
import noesis, rapi  # type: ignore

def registerNoesisTypes():
    
    hPak = noesis.register("Easy FPS Engine Archive", ".pak")
    noesis.setHandlerTypeCheck(hPak, ChkArc)
    noesis.setHandlerExtractArc(hPak, LoadArc)
    return 1

def ChkArc(data):
    bs = NoeBitStream(data)
    chk = bs.readUByte()
    print(chk)
    if chk == 192:
        return 1

    
def LoadArc(fileName, fileLen, justChecking):
    data = rapi.loadIntoByteArray(fileName)
    bs  = NoeBitStream(data)
    
    if justChecking:
        return 1  
    
    E_KEY = bs.readUByte()
    F_COUNT = bs.readUInt()
    for _ in range(F_COUNT):
        FNAME_LEN = bs.readUInt()
        OFFSET = bs.readInt64()
        SIZE = bs.readInt64()
        FNAME = xorDecrypt(bs.readBytes(FNAME_LEN),E_KEY).decode('ascii')
        here = bs.tell()
        print(FNAME)
        bs.seek(OFFSET,NOESEEK_ABS)
        DAT = xorDecrypt(bs.readBytes(SIZE),E_KEY)
        rapi.exportArchiveFile(FNAME, DAT)
        bs.seek(here,NOESEEK_ABS)
    return 1    
        
    
        
        
        
def xorDecrypt(buf, keyByte):
    return bytes(b ^ keyByte for b in buf)        
    
     
    
    
    