#written by Aexadev on 11/04/26 - 12/04/26
from inc_noesis import *
import noesis, rapi # type: ignore
import os


def registerNoesisTypes():
    
    harc = noesis.register("EVOEngine Archive", ".pod")
    noesis.setHandlerTypeCheck(harc, ChkPod)
    noesis.setHandlerExtractArc(harc, LoadPod)
    
    hmdl = noesis.register("C3DModel", ".smf")
    noesis.setHandlerTypeCheck(hmdl, ChkMdl)
    noesis.setHandlerLoadModel(hmdl, LoadMdl)
    
    htex = noesis.register("EVOEngine Texture", ".raw")
    noesis.setHandlerTypeCheck(htex, ChkTex)
    noesis.setHandlerLoadRGBA(htex, LoadTex)  

    return 1

def ChkPod(data):
    bs  = NoeBitStream(data)
    val = bs.readBytes(4)
    return 1 if val == b"POD2" else 0

def ChkMdl(data):
    bs  = NoeBitStream(data)
    val = bs.readBytes(8)
    return 1 if val == b"C3DModel" else 0



def ChkTex(data):
    size = len(data)

    #if size not in (65536, 16384, 4096):
    #    return 0

    texName = rapi.getLocalFileName(rapi.getLastCheckedName())
    base = os.path.splitext(texName)[0]
    palData = rapi.loadFileOnTexturePaths(base + ".ACT")

    if palData is None:
       # print("ChkTex: palette not found:", base + ".ACT")
        return 0

    if len(palData) != 768:
       #print("ChkTex: invalid palette size")
        return 0

    return 1



def LoadPod(fileName, fileLen, justChecking):
    data = rapi.loadIntoByteArray(fileName)
    bs  = NoeBitStream(data)
    
    fNames = []

    
    #Header check
    val = bs.readBytes(4)
    if val != b"POD2":
        return 0
    
    unk1 = bs.readUInt() #hash? CRC?
    POD_DESC = _read_fixed_string(bs,80)
    FILE_COUNT = bs.readInt()
    unkCnt = bs.readInt() #count of entries of the dict/list at the end of the pod each 312 bytes
    
    #skip to paths list
    dictOffset = bs.tell()
    bs.seek(FILE_COUNT*20,NOESEEK_REL)
    for fname in range(FILE_COUNT):
        fNames.append(bs.readString())
    dataOffset = bs.tell()
    
    
    bs.seek(dictOffset,NOESEEK_ABS)
    

        
        
    print("desc: ",POD_DESC)
    print("uCnt: ",unkCnt)
    print("fCnt: ",FILE_COUNT)    
    print("dtofs: ",bs.tell())
    
    
    if justChecking:
        return 1   
    

    for fIndex in range(FILE_COUNT):
        l1 = bs.readUInt() #id?
        SIZE = bs.readUInt()
        OFFSET = bs.readUInt()
        l4 = bs.readUInt()
        l5 = bs.readUInt()
        
        here = bs.tell()
        
        
        #get file data
        bs.seek(OFFSET,NOESEEK_ABS)
        fData = bs.readBytes(SIZE)
        bs.seek(here,NOESEEK_ABS)
        
   
        #print(l1,SIZE,OFFSET,l4,l5)
        print(fNames[fIndex], " siz:",SIZE, " ofs:", OFFSET, hex(l4), hex(l5))
        rapi.exportArchiveFile(fNames[fIndex], fData)
        
        
        
        
    return 1



def LoadMdl(data, mdl_list):
    #noesis.logPopup()
    bs = NoeBitStream(data)
    rapi.rpgCreateContext() 
    rapi.rpgSetOption(noesis.RPGOPT_SWAPHANDEDNESS, 1)#LEFT HANDED
    vBuf = bytearray()
    iBuf = bytearray()
    nBuf = bytearray()
    uvBuf = bytearray()
    
    
    text = data.decode('utf-8')
    lines = text.splitlines()
    
    isV1 = False
    if lines[8] == "v1":
        isV1 = True
    print("isV1:", isV1)
    
    SPLIT_COUNT = int(lines[7].split(",")[1])  #weird even split of the entire model
    VERTEX_COUNT = int(lines[7].split(",")[0])*SPLIT_COUNT
    TRIANGLE_COUNT = int(lines[7].split(",")[2])
    print("verts: ",VERTEX_COUNT)
    print("tris: ",TRIANGLE_COUNT)
    
    if isV1:
        TEXTURE = lines[9].split(",")[5]
    else:
        TEXTURE = lines[8].split(",")[5]
    print("texture: ",TEXTURE)
    
    #VERTEXBUFFER
    s = 0 #lineshift
    if isV1 == True:
        s = 2

           
    for vi in range (VERTEX_COUNT):
        lineIdx = s + 9 + vi
        vtxdata = lines[lineIdx].split(",")
        #position
        PX = float(vtxdata[0])
        PY = float(vtxdata[1])
        PZ = float(vtxdata[2])
        #normal
        NX = float(vtxdata[3])
        NY = float(vtxdata[4])
        NZ = float(vtxdata[5])
        #uv
        U = float(vtxdata[6])
        V = float(vtxdata[7])
        
        #compile buffers
        vBuf.extend(struct.pack('fff', PX, PY, PZ))
        nBuf.extend(struct.pack('fff', NX, NY, NZ))
        uvBuf.extend(struct.pack('ff',U,V))
        


    
    for ti in range (TRIANGLE_COUNT):
        lineIdx = s + 9 + ti + VERTEX_COUNT
        tridata = lines[lineIdx].split(",")
        
        A = int(tridata[0])
        B = int(tridata[1])
        C = int(tridata[2])
        
        iBuf.extend(struct.pack('iii',A,B,C))
        
    
    texPath = ""
    basePath = rapi.getInputName()
    root = basePath
    for _ in range(2):  
        root = os.path.dirname(root)

    texPath = root +"\\ART\\"+TEXTURE
    print(texPath)
    matList = []
    mat = NoeMaterial("MAT_NAME", texPath)
    matList.append(mat)
    rapi.rpgClearBufferBinds()
    rapi.rpgSetName("mesh")  
    rapi.rpgSetMaterial("MAT_NAME") 
    rapi.rpgBindPositionBuffer(vBuf, noesis.RPGEODATA_FLOAT, 12)
    rapi.rpgBindNormalBuffer(nBuf, noesis.RPGEODATA_FLOAT, 12)
    rapi.rpgBindUV1Buffer(uvBuf, noesis.RPGEODATA_FLOAT, 8)
    rapi.rpgCommitTriangles(iBuf, noesis.RPGEODATA_UINT, TRIANGLE_COUNT*3, noesis.RPGEO_TRIANGLE)
    
    #mdl = NoeModel()
    mdl = rapi.rpgConstructModel()
    mdl.setModelMaterials(NoeModelMaterials([], matList))
    mdl_list.append(mdl)
    rapi.processCommands("-rotate 0 0 180")
    return 1



def LoadTex(data, texList):
    print("load texture init")

    size = len(data)
    #if size not in (4096, 16384, 65536):
    #    return 0

    width = height = int(size ** 0.5)

    texName = rapi.getLocalFileName(rapi.getLastCheckedName())
    base = os.path.splitext(texName)[0]

    palData = rapi.loadFileOnTexturePaths(base + ".ACT")

    if palData is None or len(palData) != 768:
        print("palette not found :", base + ".ACT")
        return 0

    palRGBA = bytearray()
    for i in range(256):
        palRGBA += bytes([
            palData[i*3+0],
            palData[i*3+1],
            palData[i*3+2],
            255
        ])

    imgRGBA = bytearray(width * height * 4)
    for i in range(width * height):
        idx = data[i]
        imgRGBA[i*4+0] = palRGBA[idx*4+0]
        imgRGBA[i*4+1] = palRGBA[idx*4+1]
        imgRGBA[i*4+2] = palRGBA[idx*4+2]
        imgRGBA[i*4+3] = palRGBA[idx*4+3]

    tex = NoeTexture(texName, width, height, imgRGBA, noesis.NOESISTEX_RGBA32)
    texList.append(tex)

    return 1


def _read_fixed_string(bs, n):
    raw = bs.readBytes(n)
    return noeAsciiFromBytes(raw)


