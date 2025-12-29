#written by Aexadev on 15/11/2025
from inc_noesis import *
import noesis, rapi # type: ignore
import binascii
import json
def registerNoesisTypes():
    
    harc = noesis.register("FlaxEngine Archive", ".flaxpac")
    noesis.setHandlerTypeCheck(harc, ChkArc)
    noesis.setHandlerExtractArc(harc, LoadRes)

    
    

    return 1

def ChkArc(data):
    bs  = NoeBitStream(data)
    val = bs.readBytes(4)
    return 1 if val == b"CFWF" else 0

def LoadRes(fileName, fileLen, justChecking):
    data = rapi.loadIntoByteArray(fileName)
    bs  = NoeBitStream(data)
    #Header check
    val = bs.readBytes(4)
    if val != b"CFWF":
        return 0
    
    VERSION = bs.readUInt()
    
    if VERSION != 9:
        er = "VERSION NOT SUPPORTED! DETECTED VERSION: " + VERSION
        noesis.doException(er)
        
    
    
    if justChecking:
        return 1   

    bs.readBytes(16)
    
    guidList = []
    typnList = []    
    
    FILE_COUNT = bs.readInt()
    for _ in range(FILE_COUNT):
        #GUID
        GUID = binascii.hexlify(bs.readBytes(16)).decode("ascii")

        TYPE_NAME = readLenUTF16(bs,64)

            #SerializedTypeNameV9 TypeName;
            #uint32 Address;
        bs.readBytes(64)
        ADDRESS = bs.readUInt()
        print(TYPE_NAME)
        print(GUID)
        
    print(bs.tell())
    
    
    

    STREAM_COUNT = bs.readInt()
    for _ in range(STREAM_COUNT):
        S_OFFSET = bs.readInt()
        S_SIZE = bs.readInt()
        S_FLAGS = bs.readInt()
        here = bs.tell()
        #print(S_OFFSET,S_SIZE,S_FLAGS)
        
        bs.seek(S_OFFSET,NOESEEK_ABS)
        if S_FLAGS:
            if S_FLAGS == 1:
                #LZ4
                DEC_SIZE = bs.readUInt()
                cd = bs.readBytes(S_SIZE-4)
                dat = rapi.decompLZ4(cd,DEC_SIZE)
        else:
            dat = bs.readBytes(S_SIZE)
        bs.seek(here,NOESEEK_ABS)
        
        bsr = NoeBitStream(dat)
        chk = bsr.readBytes(4)
        if chk == b"OggS":
            rapi.exportArchiveFile(str(_)+".ogg", dat)
            
        elif chk == b'{"ID':
            
            jsn = dat.decode("utf-8")
            ext = json.loads(jsn)["TypeName"]
            rapi.exportArchiveFile(str(_)+"_"+ext+".json", dat)  
        else:    
        
            rapi.exportArchiveFile(str(_)+".bin", dat)
    
    print(bs.tell())    


    return 1

def readLenUTF16(bs, sl):
    if sl == 0:
        return ""
    raw = bs.readBytes(sl) 
    text = raw.decode("utf-16-le", errors="ignore")
    return text.split("\x00", 1)[0]

