import maya.cmds as mc
import time
import requests
import json
import thread
from functools import partial
import hashlib
import maya.utils as utils

path=""
models = []
textures = []
hdri = []
assets = []
icons = []
APPDATA = os.getenv('APPDATA')
pathBase = APPDATA + "/Maya_PH_Cache/"
PathModels = pathBase + "ModelsIconCache/"
PathTextures = pathBase + "TxIconCache/"
PathHDRI = pathBase + "HDRIIconCache/"
vraytextures = ["Diffuse", "nor_gl", "Rough", "AO"]
state = ""
api_items = {}

class APIItem:
  def __init__(self, json):
    self.name = json["name"]
    self.tags = set(json["tags"])
    self.authors = set(json["authors"])
    self.categories = set(json["categories"])
    self.date_published = json["date_published"] # could even make this an actual python date obj!
    self.download_count = json["download_count"]
    self.type = json["type"]

  def has_tag(self, tag):
    return tag in self.tags
  def has_cat(self, cat):
    return cat in self.categories
    

class APIDatabase:
  def __init__(self, json):
    self.db = {}
    self.all_tags = set()

    for item in json.items():
      api_item = APIItem(item[1])  
      self.db[item[0]] = api_item
      self.all_tags = self.all_tags.union(api_item.tags)

  def find_by_name(self, query):
    query_lower = query.lower()
    returned_items = []
    for item in self.db.values():
      if query_lower in item.name:
        returned_items.append(item)
    return returned_items
class dynamicLoad():
    def deletebuttons(self, wtf):
        print(wtf)
        print(icons)
        for a in icons:
            cmds.deleteUI(a, ctl=True)
        global icons
        icons = []
    def __init__(self):
        #-- Window
        
        self.window_name = 'PHAPI'
        if (mc.window(self.window_name, exists=True)):
                mc.deleteUI(self.window_name)
        self.window = mc.window(self.window_name, title='Poly Haven Maya API')

        #-- Layout
        
        frame = cmds.frameLayout('imageFrame', label='Assets', borderStyle='in',w = 100, h = 100 )
        cmds.columnLayout('rlRun', columnAttach=('both', 5), rowSpacing=10, columnWidth=250, adj=1)
        cmds.rowColumnLayout( numberOfRows=4, rowHeight=[(1, 30), (2, 30)] )
        cmds.button( label='Get Api Data', command=getapidata )
        updatebox = cmds.checkBox("updatebox", label='Update/Redownload' )
        cmds.button( label='RefreshList', command=self.refreshlist )
        self.Chan = cmds.optionMenu( label='Asset Channel', cc=self.refreshlist)
        cmds.menuItem( label='Textures' )
        cmds.menuItem( label='Model' )
        cmds.menuItem( label='HDRI' )
        cmds.button( label='Set Cache Dir', command=self.setcachedir )
        self.TFCache = cmds.textField(tx="Test")
        cmds.rowLayout(numberOfColumns=4, columnWidth2=(90, 80))
        self.resselector = cmds.optionMenu( label='Resolution')
        cmds.menuItem( label='1k' )
        cmds.menuItem( label='2k' )
        cmds.menuItem( label='4k' )
        cmds.menuItem( label='8k' )
        cmds.text( label='Search' )
        self.searchbox = cmds.textField(cc=self.runsearch)
        tagbox = cmds.checkBox("tagbox", label='Tag/Category Search' )
        scrollLay = cmds.scrollLayout( horizontalScrollBarThickness=32, verticalScrollBarThickness=32, p=frame, cr=True)
        layout = mc.formLayout(w=700)
        
        self.gridview = mc.gridLayout(
                numberOfColumns=4,
                cellWidthHeight=(164, 164),
                allowEmptyCells=False,
                autoGrow=True,
                p = scrollLay,
                cr=True
            )
        

        #-- Load buttons
        getapidata(False)
        self.create_buttons()
        
        mc.showWindow( self.window_name )
     
    def runsearch(self, wtf):
        SearchPhrase = cmds.textField(self.searchbox, query=True, text=True)
        print(SearchPhrase)
        Chad = cmds.optionMenu(self.Chan, query=True, value=True)
        self.load_button(Chad, SearchPhrase)
	    
    def create_buttons(self):
        self.load_button("Textures", "")
    def refreshlist(self, wtf):
        self.deletebuttons(False)
        Chad = cmds.optionMenu(self.Chan, query=True, value=True)
        self.load_button(Chad, "")
        for item in cmds.optionMenu(self.resselector, q=True, ill=True) or []:
            cmds.deleteUI(item)
        if state == "HDRI":
            cmds.menuItem( label='1k', p=self.resselector)
            cmds.menuItem( label='2k', p=self.resselector)
            cmds.menuItem( label='4k', p=self.resselector)
            cmds.menuItem( label='8k', p=self.resselector)
            cmds.menuItem( label='16k', p=self.resselector)
        else:
            cmds.menuItem( label='1k', p=self.resselector)
            cmds.menuItem( label='2k', p=self.resselector)
            cmds.menuItem( label='4k', p=self.resselector)
            cmds.menuItem( label='8k', p=self.resselector)
    def AssetCallback(self, name, type):
        print(type)
        Diffuse = ""
        Normal = ""
        Roughness = ""
        AO = ""
        Reso = cmds.optionMenu(self.resselector, query=True, value=True)
        print(Reso)
        print(name)
        #name = 'aerial_asphalt_01'
        filesrequest = requests.get("https://api.polyhaven.com/files/{0}".format(name))
        if type == "Textures":
            for tex in vraytextures:
                print(tex)
                url = filesrequest.json()[tex][Reso]['png']['url']
                remotehash = filesrequest.json()[tex][Reso]['png']['md5']
                DownloadPath = pathBase + "Textures/" + name + "/" + Reso + "/"
                if not os.path.exists(DownloadPath):
                    os.makedirs(DownloadPath)
                    print("The new directory is created!")
                filepath = DownloadPath + os.path.basename(url)
                print(url)
                print(filepath)
                if not os.path.exists(filepath):
                    img_data = requests.get(url)
                    if img_data.status_code == 200:        
                        with open(filepath, 'wb') as f:
                            f.write(img_data.content)
                    downloadedhash = hashlib.md5(open(filepath,'rb').read()).hexdigest()
                    if remotehash == downloadedhash:
                        print("Download good")
                    else:
                        print("awww fug")
                if tex == "Diffuse":
                    Diffuse = filepath
                elif tex == "nor_gl":
                    Normal = filepath
                elif tex == "Rough":
                    Roughness = filepath
                elif tex == "AO":
                    AO = filepath
            CreateVrayShader(name, Diffuse, Normal, Roughness, AO)
        elif type == "HDRI":
            
            url = filesrequest.json()['hdri'][Reso]['exr']['url']
            remotehash = filesrequest.json()['hdri'][Reso]['exr']['md5']
            filesize = filesrequest.json()['hdri'][Reso]['exr']['size']
            DownloadPath = pathBase + "HDRI/" + name + "/" + Reso + "/"
            if not os.path.exists(DownloadPath):
                os.makedirs(DownloadPath)
                print("The new directory is created!")
            filepath = DownloadPath + os.path.basename(url)
            print(url)
            print(filepath)
            if not os.path.exists(filepath):
                print("ze")
                gMainProgressBar = maya.mel.eval('$tmp = $gMainProgressBar');
                cmds.progressBar( gMainProgressBar,	edit=True, beginProgress=True, isInterruptable=True, status='"Example Calculation ...',	maxValue=filesize )
                img_data = requests.get(url, stream=True)
                print("be")
                if img_data.status_code == 200:        
                    with open(filepath, 'wb') as f:
                        for data in img_data.iter_content(1024):
                            cmds.progressBar(gMainProgressBar, edit=True, step=len(data))
                            f.write(data)
                cmds.progressBar(gMainProgressBar, edit=True, endProgress=True)
                downloadedhash = hashlib.md5(open(filepath,'rb').read()).hexdigest()
                if remotehash == downloadedhash:
                    print("Download good")
                else:
                    print("awww fug")
            if not cmds.objExists('PH_Dome'):
                fileNode = cmds.shadingNode('file', at=1)
                cmds.rename(fileNode, 'PHDome_Map')
                Dome = cmds.shadingNode('VRayLightDomeShape', al=1)
                cmds.setAttr(Dome + '.useDomeTex', 1)
                cmds.connectAttr('PHDome_Map.outColor', Dome + '.domeTex')
                cmds.rename(Dome, 'PH_Dome')
            print(filepath)
            cmds.setAttr('PHDome_Map.fileTextureName', filepath, type = 'string')
    def setcachedir(self, why):
        global pathBase
        pathBase = cmds.fileDialog2(fm=2)[0].encode("utf-8") + "/"
        cmds.textField(self.TFCache, edit=True, tx=pathBase)
        print(pathBase)
    def load_button(self, type, Search):
        if icons:
            print("Shid")
            self.deletebuttons(False)
        global state
        if type == "Model":
            state = "Model"
            pathIcons = PathModels
        elif type == "HDRI":
            state = "HDRI"
            pathIcons = PathHDRI
        else:
            state = "Textures"
            pathIcons = PathTextures
        tagValue = cmds.checkBox('tagbox', query=True, value=True)
        print(Search)
        print("Tag")
        print(tagValue)
        if Search == "":
            for (dirpath, dirnames, filenames) in os.walk(pathIcons):
                for fullname in filenames:
                    name = os.path.splitext(fullname)[0]
                    mc.setParent( self.gridview )
                    mixedpath = pathIcons + fullname
                    temp = mc.iconTextButton( style='iconAndTextVertical', label=name, image=mixedpath, c=partial(self.AssetCallback, name, type))
                    icons.append(temp)
        elif Search is not None and tagValue:
           for (dirpath, dirnames, filenames) in os.walk(pathIcons):
                for fullname in filenames:
                    name = os.path.splitext(fullname)[0]
                    if not api_items[name].has_tag(Search) and not api_items[name].has_cat(Search):
                        continue 
                    mc.setParent( self.gridview )
                    mixedpath = pathIcons + fullname
                    temp = mc.iconTextButton( style='iconAndTextVertical', label=name, image=mixedpath, c=partial(self.AssetCallback, name, type))
        elif Search is not None:
           for (dirpath, dirnames, filenames) in os.walk(pathIcons):
                for fullname in filenames:
                    if Search not in fullname:
                        continue
                    name = os.path.splitext(fullname)[0]
                    mc.setParent( self.gridview )
                    mixedpath = pathIcons + fullname
                    temp = mc.iconTextButton( style='iconAndTextVertical', label=name, image=mixedpath, c=partial(self.AssetCallback, name, type))
                    icons.append(temp)
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '?', autosize = False):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    styling = '%s |%s| %s%% %s' % (prefix, fill, percent, suffix)
    if autosize:
        cols, _ = shutil.get_terminal_size(fallback = (length, 1))
        length = cols - len(styling)
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s' % styling.replace(fill, bar))
    # Print New Line on Complete
    if iteration == total: 
        print()
def jprint(obj):
    # create a formatted string of the Python JSON object
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)
def grabAllIcons():
    i = 0
    mpber = len(models)
    tpber = len(textures)
    hpber = len(hdri)
    for m in models:
        path = PathModels + "{0}.png".format(m)
        printProgressBar(i, mpber, prefix = 'Models:', suffix = 'Complete', length = 50)
        if os.path.exists(path):
            print(m)
    
        if not os.path.exists(path):
            
            url = "https://cdn.polyhaven.com/asset_img/thumbs/{0}.png?width=125&height=125".format(m)
            img_data = requests.get(url)
            if img_data.status_code == 200:        
                with open(path, 'wb') as f:
                    f.write(img_data.content)
        i += 1
    print("Model Icons Done")
    i = 0
    for t in textures:
        path = PathTextures + "{0}.png".format(t)
        printProgressBar(i, tpber, prefix = 'Textures:', suffix = 'Complete', length = 50)
        if os.path.exists(path):
            print(t)
        if not os.path.exists(path):
            
            url = "https://cdn.polyhaven.com/asset_img/thumbs/{0}.png?width=125&height=125".format(t)
            img_data = requests.get(url)
            if img_data.status_code == 200:        
                with open(path, 'wb') as f:
                    f.write(img_data.content)
        i += 1
    i = 0
    for h in hdri:
        path = PathHDRI + "{0}.png".format(h)
        printProgressBar(i, hpber, prefix = 'Hdri:', suffix = 'Complete', length = 50)
        if os.path.exists(path):
            print(h)
        if not os.path.exists(path):
            url = "https://cdn.polyhaven.com/asset_img/thumbs/{0}.png?width=125&height=125".format(h)
            img_data = requests.get(url)
            if img_data.status_code == 200:        
                with open(path, 'wb') as f:
                    f.write(img_data.content)
        i += 1
def getapidata(bools):
    if not os.path.exists(pathBase):
        os.makedirs(PathModels)
        print("The new directory is created!")
    updateboxValue = cmds.checkBox('updatebox', query=True, value=True)
    print(updateboxValue)
    print(pathBase)
    jsonpth = pathBase + "PH_API.json"
    if not os.path.exists(jsonpth) or updateboxValue:
        print("Reget")
        response2 = requests.get("https://api.polyhaven.com/assets")
        with open(jsonpth, 'w') as outfile:
            json.dump(response2.json(), outfile)
    with open(jsonpth) as json_file:
        APIJson = json.load(json_file)
    for item in APIJson.items():
        global api_items
        api_items[item[0]] = APIItem(item[1])
    for a in api_items.values():
        if a.type == 0:
            print(a.name)
            hdri.append(a.name)
        if a.type == 1:
            textures.append(a.name)
        if a.type == 2:
            models.append(a.name)
    return
    if not os.path.exists(PathModels):
        os.makedirs(PathModels)
        print("The new directory is created!")
    if not os.path.exists(PathTextures):
        os.makedirs(PathTextures)
        print("The new directory is created!")
    if not os.path.exists(PathHDRI):
        os.makedirs(PathHDRI)
        print("The new directory is created!")
    grabAllIcons()
    print(models)
    print(i)
dynamicLoad()
def connectPlace2DToFileNode(place2dTextureNode, fileNode):
    cmds.connectAttr ((place2dTextureNode + ".coverage"), (fileNode + ".coverage"))
    cmds.connectAttr ((place2dTextureNode + ".translateFrame"), (fileNode + ".translateFrame"))
    cmds.connectAttr ((place2dTextureNode + ".rotateFrame"), (fileNode + ".rotateFrame"))
    cmds.connectAttr ((place2dTextureNode + ".mirrorU"), (fileNode + ".mirrorU"))
    cmds.connectAttr ((place2dTextureNode + ".mirrorV"), (fileNode + ".mirrorV"))
    cmds.connectAttr ((place2dTextureNode + ".stagger"), (fileNode + ".stagger"))
    cmds.connectAttr ((place2dTextureNode + ".wrapU"), (fileNode + ".wrapU"))
    cmds.connectAttr ((place2dTextureNode + ".wrapV"), (fileNode + ".wrapV"))
    cmds.connectAttr ((place2dTextureNode + ".repeatUV"), (fileNode + ".repeatUV"))
    cmds.connectAttr ((place2dTextureNode + ".offset"), (fileNode + ".offset"))
    cmds.connectAttr ((place2dTextureNode + ".rotateUV"), (fileNode + ".rotateUV"))
    cmds.connectAttr ((place2dTextureNode + ".noiseUV"), (fileNode + ".noiseUV"))
    cmds.connectAttr ((place2dTextureNode + ".vertexUvOne"), (fileNode + ".vertexUvOne"))
    cmds.connectAttr ((place2dTextureNode + ".vertexUvTwo"), (fileNode + ".vertexUvTwo"))
    cmds.connectAttr ((place2dTextureNode + ".vertexUvThree"), (fileNode + ".vertexUvThree"))
    cmds.connectAttr ((place2dTextureNode + ".vertexCameraOne"), (fileNode + ".vertexCameraOne"))
    cmds.connectAttr ((place2dTextureNode + ".outUV"), (fileNode + ".uv"))
    cmds.connectAttr ((place2dTextureNode + ".outUvFilterSize"), (fileNode + ".uvFilterSize"))
def CreateVrayShader(name, Diffuse, Normal, Roughness, AO):
    aoCheck = False
    VrayShader = cmds.shadingNode('VRayMtl', asShader=True, n=name)
    shaderGrp = cmds.sets(renderable=True, noSurfaceShader=True, name = (VrayShader + "_SG"))
    cmds.connectAttr((VrayShader + ".outColor"), (shaderGrp + ".surfaceShader"))
    place2dTextureNode=cmds.shadingNode("place2dTexture", asUtility=True)
    fileNode = cmds.shadingNode("file", asTexture=True)
    cmds.setAttr((fileNode + ".filterType"), 0)
    connectPlace2DToFileNode(place2dTextureNode, fileNode)
    if AO == "":
        cmds.connectAttr ((fileNode + ".outColor"), (VrayShader + ".diffuseColor"))
    else:
        layerTex = cmds.shadingNode("VRayLayeredTex", asTexture=True)
        cmds.connectAttr ((fileNode + ".outColor"), (layerTex + ".layers[0].tex")) 
    cmds.setAttr(fileNode + ".fileTextureName", Diffuse, type="string")
    if not AO == "":
        fileNode = cmds.shadingNode("file", asTexture=True)
        cmds.setAttr((fileNode + ".filterType"), 0)
        connectPlace2DToFileNode(place2dTextureNode, fileNode)
        cmds.connectAttr ((fileNode + ".outColor"), (layerTex + ".layers[1].tex"))
        cmds.connectAttr ((layerTex + ".outColor"), (VrayShader + ".diffuseColor")) 
        cmds.setAttr ((layerTex + ".layers[1].blendMode"), 5)
        cmds.setAttr(fileNode + ".fileTextureName", AO, type="string")
    fileNode = cmds.shadingNode("file", asTexture=True)
    cmds.setAttr((fileNode + ".filterType"), 0)
    connectPlace2DToFileNode(place2dTextureNode, fileNode)
    cmds.setAttr ((fileNode + ".alphaIsLuminance"), 1) 
    cmds.connectAttr ((fileNode + ".outAlpha"), (VrayShader + ".reflectionGlossiness"))
    cmds.setAttr(fileNode + ".fileTextureName", Roughness, type="string")
    cmds.setAttr((VrayShader + ".useRoughness"), 1)
    cmds.setAttr((VrayShader + ".reflectionColor"), 1,1,1, type="double3")
    cmds.setAttr ((fileNode + ".colorSpace"), "Raw", type="string")
    fileNode = cmds.shadingNode("file", asTexture=True)
    cmds.setAttr((fileNode + ".filterType"), 0)
    connectPlace2DToFileNode(place2dTextureNode, fileNode)
    cmds.connectAttr ((fileNode + ".outColor"), (VrayShader + ".bumpMap"))
    cmds.setAttr ((VrayShader + ".bumpMapType"), 1)
    cmds.setAttr(fileNode + ".fileTextureName", Normal, type="string")
    cmds.setAttr ((fileNode + ".colorSpace"), "Raw", type="string")