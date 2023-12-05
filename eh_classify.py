import sys
import os
import re
import json

dbName = "db.text.json"
dbName_artist = "artist.db.text.json"
dbName_group = "group.db.text.json"
myDBName = "db.lists.json"
unsortDir = "unsort"
# 初始化参数
def Init():
    global argv,mangaPath,targetPath,fileList
    argv = sys.argv
    argvNumber = len(argv)
    #根据输入的参数判断下一步操作
    if argvNumber == 1 or argv[1] == "help":
        help()
        exit()
    if argvNumber >= 2 and argv[1] == "newdb":
        print("接收到newdb参数，创建新的",myDBName,"文件")
        CreatDB()
        exit()
    if argvNumber >= 3 and argv[1] == "-s":
        print("搜索关键字：",argv[2],"\nps：有空格的关键字需要用双引号括起来")
        SearchAll(argv[2])
        exit()
    if argvNumber >= 2:
        if os.path.isdir(argv[1]): # 如果第1个参数为目录
            mangaPath = argv[1]
            targetPath = mangaPath
            fileList = os.listdir(mangaPath)
            print("第一个参数为",mangaPath)
            if len(fileList) == 0:
                print("目录为空，退出脚本")
                exit()
        else:
            print("出错：第一个参数不为目录")
    if argvNumber >= 3: # 如果有2个以上参数
        if os.path.isdir(argv[2]):  # 如果第2个参数为目录
            targetPath = argv[2]
            print("第二个参数为",targetPath)
        else:
            print("出错：第二个参数不为目录")
            exit()

def GetMangaList():
    global mangaList
    mangaList = []
    for file in fileList:
        file_path = os.path.join(mangaPath,file)
        if os.path.isfile(file_path):
            mangaList.append(file)
    if len(mangaList) == 0:
        print("目标目录下没有文件（不支持文件夹），退出脚本")
        exit()
    else:
        print("获取到文件个数：",len(mangaList))

def ImportDB(): # 导入db数据
    global allArtists,allGroups
    if not os.path.exists(myDBName):
        CreatDB()
    with open(myDBName,"r",encoding="utf-8") as d:
        myDB = json.load(d)
        allArtists = myDB["artist"]
        allGroups = myDB["group"]

def HandleMangaList():
    matchArtists = r"\[(.*?)\]"
    matchGroup = r"\((.*?)\)"
    for mangaTitle in mangaList:
        print("===================================================================================")
        print("当前处理文件：",mangaTitle)
        oPath = os.path.join(mangaPath,mangaTitle)
        artists = re.findall(matchArtists,mangaTitle,flags=0)
        if artists:
            artists = artists[0].strip()
            print("匹配到作者名：",artists)
            groupName = re.findall(matchGroup,artists,flags=0)
            if groupName: #如果有团队
                groupName = groupName[0]
                artists = artists.replace("(" + groupName + ")","").strip()
                groupName = groupName.strip()
                print("匹配到团队名：",groupName)
                print("处理后作者名：",artists)
            result = GetSortPath(artists,groupName)
            print("匹配数据库结果：",result)
            if "group" in result:
                gPath = os.path.join(targetPath,"group",result["group"],mangaTitle)
                print("移动到团队分类：",gPath)
                MoveFile(oPath,gPath)
            if "artist" in result:
                aPath = os.path.join(targetPath,"artist",result["artist"],mangaTitle)
                print("移动到作者分类：",aPath)
                MoveFile(oPath,aPath)
            if result == {}:
                tPath = os.path.join(targetPath,unsortDir,mangaTitle)
                print("未在数据库中匹配到作者名或团队，移动到",tPath)
                MoveFile(oPath,tPath)
        else:
            tPath = os.path.join(targetPath,unsortDir,mangaTitle)
            print("没有在文件名中匹配到作者，移动到",tPath)
            MoveFile(oPath,tPath)
        print("===================================================================================")

def GetSortPath(artist,group):
    result = {}
    # 进入这个函数必定有匹配到作者,首先在作者字典中查找是否有匹配目标作者名的字符串
    for key,value in allArtists.items():
        if artist.lower() == key or artist.lower() == value:
            result["artist"] = key
            break
    if not "artist" in result: # 如果字典中没有对应的key，说明作者字典中没有目标字符串，继续在团队字典中查找
        for key,value in allGroups.items():
            if artist.lower() == key or artist.lower() == value:
                result["group"] = key
                break
    if group: # 如果有团队名
        if not "group" in result:
            for key,value in allGroups.items():
                if group.lower() == key or group.lower() == value:
                    result["group"] = key
                    break
        if not "artist" in result:
            for key,value in allArtists.items():
                if group.lower() == key or group.lower() == value:
                    result["artist"] = key
                    break
    return result

def IsAllAscii(s):  # 判断字符串是否全是ascii码，即可能为罗马音
    if s == re.findall("[\x00-\x7F]+")[0]:
        return True
    else:
        return False

def MoveFile(filePath,sortPath):
    try:
        if os.path.exists(sortPath):
            print("文件已存在：",sortPath)
            return
        dirName = os.path.dirname(sortPath)
        if not os.path.exists(dirName):
            os.makedirs(dirName)
        os.link(filePath, sortPath)
    except:
        print("创建硬链接失败")
        #exit()


def CreatDB():
    try:
        dbPath = os.path.join(os.path.dirname(os.path.abspath(__file__)),dbName) # 获取db的路径
        with open(dbPath,"r",encoding="utf-8") as dbFile: # 打开db
            db = json.load(dbFile) # 读取并解析json
        for item in db["data"]:
            if item["namespace"] == "artist":
            #     if not os.path.exists(dbName_artist): # 将db中的artist和group单独提取到文件
            #         with open(dbName_artist, "w",encoding="utf-8") as a:
            #             json.dump(item, a,ensure_ascii=False)
                artistDB = item
            if item["namespace"] == "group":
                # if not os.path.exists(dbName_group):
                #     with open(dbName_group, "w",encoding="utf-8") as g:
                #         json.dump(item, g,ensure_ascii=False)
                groupDB = item
        # 将artist和group中的作者/团队的key和'name'对应的value使用lower处理，并单独提取到文件
        artistDict = artistDB["data"]
        groupDict = groupDB["data"]
        aDict = {}
        gDict = {}
        for key,value in artistDict.items():
            aDict[key.lower()] = value["name"].lower()
        for key,value in groupDict.items():
            gDict[key.lower()] = value["name"].lower()
        dbLists = {"artist":aDict,"group":gDict}
        with open(myDBName, "w",encoding="utf-8") as dbl:
            json.dump(dbLists, dbl,ensure_ascii=False)
    except:
        print("创建json文件出错")

def SearchAll(keyword):
    ImportDB()
    red = "\033[31m"
    end = "\033[0m"
    full = {}
    result = {}
    result["artist"] = []
    result["group"] = []
    for key,value in allArtists.items():
        if re.search(keyword,key,flags=re.I):
            result["artist"].append(key)
        if re.search(keyword,value,flags=re.I):
            result["artist"].append(value)
        if key.lower() == keyword.lower():
            full["artist"] = key
        if value.lower() == keyword.lower():
            full["artist"] = value      
    for key,value in allGroups.items():
        if re.search(keyword,key,flags=re.I):
            result["group"].append(key)
        if re.search(keyword,value,flags=re.I):
            result["group"].append(value)
        if key.lower() == keyword.lower():
            full["group"] = key
        if value.lower() == keyword.lower():
            full["group"] = value
    print("完全匹配的对象有：",full)
    print("匹配的对象有：",result)

# 帮助
def help():
    print("*用法:\n    python3 eh_classify.py mangaPath [targetPath]")
    print("*帮助:\n    python3 eh_classify.py help")
    print("*说明:\n    mangaPath 漫画所在的目录绝对/相对路径,只会读取其中的文件,不会读取子文件夹;\n    targetPath 可选参数,默认等于mangaPath,分类好的漫画存放目录;\n    分类规则:\n        1.使用硬链接,如果失败则跳过该文件;\n        2.分别根据作者名和团队名进行分类,分类后放在targetPath/artist/作者名和targetPath/artist/团队名路径下,整理失败的放在targetPath/artist/其它;\n        3.根据文件名自动识别作者,格式为(其它信息)[作者名(团队名)]标题...,识别出的作者名/团队名会进一步在db.text.json中查找,避免[团队名(作者名)]格式的文件分类错误,并且会使用db中的日文名进行分类,如果在db中无法找到,则按失败处理\n        4.如果使用了新的db.text.json，先执行python3 eh_classify.py newdb更新下数据\n        5.使用python3 eh_classify.py -s keyword 查找db中是否有能匹配的作者")


if __name__ == '__main__':
    Init()
    GetMangaList()
    ImportDB()
    HandleMangaList()
