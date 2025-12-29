#written by Aexadev on 02/11/2025 - 02/11/2025
from inc_noesis import *
import noesis, rapi # type: ignore

def registerNoesisTypes():
    
    harc = noesis.register("GodotEngine Archive", ".pck")
    noesis.setHandlerTypeCheck(harc, ChkArc)
    noesis.setHandlerExtractArc(harc, LoadRes)
    

    return 1

def ChkArc(data):
    bs  = NoeBitStream(data)
    val = bs.readBytes(4)
    return 1 if val == b"GDPC" else 0



#https://github.com/godotengine/godot/blob/0fdbf050e0c7fc7e0a9d42c2a41ee3bfdffbd8f1/core/io/file_access_pack.cpp
def LoadRes(fileName, fileLen, justChecking):
    data = rapi.loadIntoByteArray(fileName)
    bs  = NoeBitStream(data, NOE_LITTLEENDIAN)

    magic = bs.readBytes(4)
    if magic != b"GDPC":
        return 0
    pck_start = bs.tell() - 4   

    if justChecking:
        return 1

    version    = bs.readUInt()
    ver_major  = bs.readUInt()
    ver_minor  = bs.readUInt()
    ver_patch  = bs.readUInt()
    print("version:", version, ver_major, ver_minor, ver_patch)

    pack_flags = bs.readUInt()
    file_base  = bs.readInt64()

    PACK_DIR_ENCRYPTED = 1 << 0
    PACK_REL_FILEBASE  = 1 << 1
    PACK_SPARSE_BUNDLE = 1 << 2

    if version == 3 or (version == 2 and (pack_flags & PACK_REL_FILEBASE)):
        file_base += pck_start

    if version == 3:
        dir_offset = bs.readInt64() + pck_start
        bs.seek(dir_offset, NOESEEK_ABS)
    elif version == 2:
        bs.readBytes(64)  # reserved

    if pack_flags & PACK_DIR_ENCRYPTED:
        print("encrypted !")
        return 0

    file_count = bs.readUInt()
    print("file count:", file_count)

    for _ in range(file_count):
        name = readLenStr(bs)           
        ofs  = bs.readInt64()
        size = bs.readInt64()
        md5  = bs.readBytes(16)
        flags = bs.readUInt()

        real_ofs = file_base + ofs      

        print(name, hex(real_ofs), size, hex(flags))

        here = bs.tell()


        PACK_FILE_ENCRYPTED = 1 << 0 
        if flags & PACK_FILE_ENCRYPTED:
            print("file is encrypted!!")
        else:
            bs.seek(real_ofs, NOESEEK_ABS)
            blob = bs.readBytes(size)
            rapi.exportArchiveFile(name, blob)

        bs.seek(here, NOESEEK_ABS)

    return 1


def readLenStr(bs):
    sl = bs.readUInt()
    if sl == 0:
        return ""
    raw = bs.readBytes(sl)
    return raw.split(b"\x00", 1)[0].decode("ascii", "ignore")


