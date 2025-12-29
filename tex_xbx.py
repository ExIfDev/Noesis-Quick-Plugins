#Written by Aexadev on 28/09/2025

from inc_noesis import *  

def registerNoesisTypes():
    handle = noesis.register("Xbox texture", ".xbx")
    noesis.setHandlerTypeCheck(handle, xbxCheckType)
    noesis.setHandlerLoadRGBA(handle, xbxLoadRGBA)
    return 1

def xbxCheckType(data):
    if len(data) < 4:
        return 0
    bs = NoeBitStream(data)
    magic = bs.readBytes(4)
    return 1 if magic == b"XPR0" else 0 

def xbxLoadRGBA(bs,texList):
    bs = NoeBitStream(bs)
    bs.seek(4, NOESEEK_ABS)
    DATA_SIZE = bs.readUInt()
    DATA_OFFSET = bs.readUShort()
    bs.seek(11, NOESEEK_ABS)
    WIDTH = bs.readUShort()
    bs.seek(14, NOESEEK_ABS)
    BPP= bs.readUShort()
    HEIGHT = WIDTH
    bs.seek(DATA_OFFSET, NOESEEK_ABS)
    imageRaw = bs.readBytes(DATA_SIZE-DATA_OFFSET)
    #rgbamo = rapi.imageFromMortonOrder(imageRaw, WIDTH, HEIGHT, BPP) 
    rgba = rapi.imageDecodeRaw(imageRaw, WIDTH, HEIGHT, "b8g8r8a8")
    tex = NoeTexture("_tex", WIDTH, HEIGHT, rgba, noesis.NOESISTEX_RGBA32)
    texList.append(tex)
    return 1
    
    
    
    

