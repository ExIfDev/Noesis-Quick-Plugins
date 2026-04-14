#written by Aexadev on 14/04/26
from inc_noesis import *
import noesis, rapi # type: ignore
import os


def registerNoesisTypes():
    
    harc = noesis.register("MENG Engine Archive", ".mpk")
    noesis.setHandlerTypeCheck(harc, ChkPak)
    noesis.setHandlerExtractArc(harc, LoadPak)
    

    return 1

def ChkPak(data):
    bs  = NoeBitStream(data)
    val = bs.readBytes(4)
    return 1 if val == b"MENG" else 0



def LoadPak(fileName, fileLen, justChecking):
    data = rapi.loadIntoByteArray(fileName)
    bs  = NoeBitStream(data)
    
    fNames = []
    noesis.logPopup()
    
    #Header check
    val = bs.readBytes(4)
    if val != b"MENG":
        return 0
    
    PAK_VER = bs.readBytes(4)#xV4\0x12
    RES_TYP = bs.readBytes(4)#PACK
    bs.seek(28,NOESEEK_REL) #unk
    
    FILE_COUNT = bs.readUInt()
    DICT_OFFSET = bs.readUInt()
    unkm1 = bs.readInt()
    unkm2 = bs.readInt()#3
    print("fCnt: ",FILE_COUNT)
    

    if justChecking:
        return 1  
    
     
    bs.seek(DICT_OFFSET,NOESEEK_ABS)
    for f in range(FILE_COUNT):
        unk1 = bs.readInt()
        ASSET_TYPE = _read_fixed_string(bs,12).rstrip("\0")
        unk2 = bs.readInt() #0x20 maybe compression type??
        C_CRC = bs.readInt() #CRC possibly
        REAL_SIZ = bs.readInt() 
        COMP_SIZ = bs.readInt() 
        OFFSET = bs.readInt() 
        
        here = bs.tell()
        
        bs.seek(OFFSET, NOESEEK_ABS)
        if COMP_SIZ == REAL_SIZ:
            dData = bs.readBytes(REAL_SIZ)
        else:
            D_CRC = bs.readInt()
            cData = bs.readBytes(COMP_SIZ - 4)
            dData = meng_decompress(cData, REAL_SIZ)
        bs.seek(here, NOESEEK_ABS)
  
        print("id: ",unk1, "typ: ",ASSET_TYPE, unk2, hex(C_CRC), "rSiz: ",REAL_SIZ, "cSiz: ",COMP_SIZ ,"off: ",OFFSET)

        rapi.exportArchiveFile(str(hex(unk1))+"."+ASSET_TYPE, dData)
        
        
        
    return 1


def _read_fixed_string(bs, n):
    raw = bs.readBytes(n)
    return noeAsciiFromBytes(raw)

#sub_4C1550
def meng_decompress(src, dst_size):
    src = bytearray(src)
    dst = bytearray(dst_size)

    p = 0
    dp = 0
    dst_end = dst_size

    if len(src) < 2:
        raise IOError("src not enough")

    while True:
        if p + 1 >= len(src):
            raise IOError("expected token")

        opcode = src[p]
        nxt = src[p + 1]

        if opcode & 0x80:
            if (opcode & 0xE0) == 0x80:
                length = (opcode & 0x1F) + 1
                copy_src = p + 1
                ref = -1
                p = p + 1 + length

            elif (opcode & 0xC0) == 0xC0:
                length = (opcode & 0x3F) + 4
                ref = dp - nxt - 1
                copy_src = -1
                p = p + 2

            else:
                x = nxt | ((opcode & 0x0F) << 8)

                if (opcode & 0xF0) == 0xA0:
                    length = x + 32
                    copy_src = p + 2
                    ref = -1
                    p = p + 2 + length
                else:
                    if p + 3 >= len(src):
                        raise IOError("not enough data")
                    off = (src[p + 2] << 8) | src[p + 3]
                    length = x + 6
                    ref = dp - off - 1
                    copy_src = -1
                    p = p + 4
        else:
            off = opcode & 0x0F
            length = (opcode >> 4) + 3
            ref = dp - off - 1
            copy_src = -1
            p = p + 1
        end_dp = dp + length
        final_token = (end_dp >= dst_end)
        if end_dp > dst_end:
            length = dst_end - dp

        if copy_src >= 0:
            if copy_src + length > len(src):
                raise IOError("not enough data")
            i = 0
            while i < length:
                dst[dp] = src[copy_src + i]
                dp += 1
                i += 1
        else:
            if ref < 0:
                raise IOError("inv bref")
            i = 0
            while i < length:
                dst[dp] = dst[ref]
                dp += 1
                ref += 1
                i += 1

        if final_token or dp >= dst_end:
            break

    return dst