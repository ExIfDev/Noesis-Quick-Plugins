# Written by Aexadev on 28/09/2025
# Blaster Master Zero 2

from inc_noesis import *


def registerNoesisTypes():
    handle = noesis.register("Blaster Master Zero 2 texture", ".osb")
    noesis.setHandlerTypeCheck(handle, ChkTex)
    noesis.setHandlerLoadRGBA(handle, LoadRGBA)
    return 1


def getHdrMeta(data):
    if len(data) < 0x6C:
        return None

    bs = NoeBitStream(data)

    try:
        bs.seek(0x4C)
        TEX_OFFS = bs.readUInt()

        bs.seek(0x64)
        PLT_OFFS = bs.readUInt()
        SWP_OFFS = bs.readUInt()

        if TEX_OFFS + 0x18 > len(data):
            return None

        bs.seek(TEX_OFFS)
        PxDTA_OFS = bs.readUInt()
        PXDTA_SIZ = bs.readUInt()
        bs.readUInt()#unk
        WIDTH = bs.readUInt()
        HEIGHT = bs.readUInt()
        bs.readUInt()#??

        if WIDTH <= 0 or HEIGHT <= 0:
            return None
        if PXDTA_SIZ != WIDTH * HEIGHT * 4:
            return None
        if PxDTA_OFS + PXDTA_SIZ > len(data):
            return None
        if PLT_OFFS + 0x400 > len(data):
            return None

        return TEX_OFFS, PLT_OFFS, SWP_OFFS, PxDTA_OFS, PXDTA_SIZ, WIDTH, HEIGHT
    except:
        return None


def ChkTex(data):
    return 1 if getHdrMeta(data) else 0


def readPalette(bs, ofs, count):
    palette = []
    bs.seek(ofs)
    for i in range(count):
        b = bs.readUByte()
        g = bs.readUByte()
        r = bs.readUByte()
        a = bs.readUByte()
        palette.append((r, g, b, a))
    return palette


def LoadRGBA(data, texList):
    meta = getHdrMeta(data)
    if not meta:
        return 0

    TEX_OFS, PLT_OFS, SWP_OFS, PxDTA_OFS, PxDTA_SIZ, WIDTH, HEIGHT = meta
    bs = NoeBitStream(data)
    plt = readPalette(bs, PLT_OFS, 256)

    if SWP_OFS and SWP_OFS + 0x2C <= len(data):
        bs.seek(SWP_OFS + 0x24)
        CLR_CNT = bs.readUInt()
        CLR_RELOFS = bs.readUInt()
        CLR_OFS = SWP_OFS + CLR_RELOFS

        if 0 < CLR_CNT <= 256 and CLR_OFS + CLR_CNT * 4 <= len(data):
            swap = readPalette(bs, CLR_OFS, CLR_CNT)
            cnt = 0
            for b in range(0, 256, CLR_CNT):
                end = min(b + CLR_CNT, 256)
                hasColor = False
                for i in range(b, end):
                    r, g, b, a = plt[i]
                    if r or g or b:
                        hasColor = True
                        break
                if hasColor:
                    break
                cnt = end
            if cnt == 0:
                cnt = CLR_CNT
            for i in range(cnt):
                plt[i] = swap[i % CLR_CNT]

    bs.seek(PxDTA_OFS)
    raw = bs.readBytes(PxDTA_SIZ)

    rgba = bytearray(PxDTA_SIZ)

    for i in range(WIDTH * HEIGHT):
        p = i * 4
        index = raw[p + 2]
        alpha = raw[p + 3]
        r, g, b, palAlpha = plt[index]
        rgba[p + 0] = r
        rgba[p + 1] = g
        rgba[p + 2] = b
        rgba[p + 3] = alpha * palAlpha // 255

    texList.append(NoeTexture("_tex", WIDTH, HEIGHT, bytes(rgba),noesis.NOESISTEX_RGBA32))
    return 1
