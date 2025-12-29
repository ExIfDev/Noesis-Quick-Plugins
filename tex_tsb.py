#Written by Aexadev on 18/10/2025

from inc_noesis import *  

def registerNoesisTypes():
    handle = noesis.register("GBO texture", ".tsb")
    noesis.setHandlerTypeCheck(handle, CheckType)
    noesis.setHandlerLoadRGBA(handle, LoadRGBA)
    return 1

def CheckType(data):
    if len(data) < 4:
        return 0
    bs = NoeBitStream(data)
    magic = bs.readBytes(4)
    return 1 if magic == b"TX2 " else 0 

def LoadRGBA(data,texList):
    bsBE = NoeBitStream(data,NOE_BIGENDIAN)
    bsBE.seek(8, NOESEEK_ABS)
    VERSION = bsBE.readUInt()
    OFFSET = bsBE.readUInt()
    SIZE = bsBE.readUInt()
    NAME = readLenStr(bsBE)
    print(NAME, VERSION, OFFSET)
    bsBE.readBytes(88) #unk
    bsBE.seek(OFFSET,NOESEEK_ABS)
    bsBE.readBytes(32) #unk
    WIDTH = bsBE.readUShort()
    HEIGHT = bsBE.readUShort()
    bsBE.readBytes(12) #unk
    print(WIDTH,HEIGHT)
    imageRaw = bsBE.readBytes(SIZE-48)
    rgba = rapi.imageDecodeDXT(imageRaw, WIDTH, HEIGHT, noesis.FOURCC_DXT5)
    tex = NoeTexture(NAME, WIDTH, HEIGHT, rgba, noesis.NOESISTEX_RGBA32)
    texList.append(tex)

    return 1
    
def readLenStr(bs):
    sl = bs.readUInt()
    if sl == 0:
        return ""
    raw = bs.readBytes(sl)
    return raw.split(b"\x00", 1)[0].decode("ascii", "ignore")    
    
    

