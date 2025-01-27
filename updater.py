from urllib.request import urlopen, urlretrieve
import json, os, re, shutil, stat, sys
from zipfile import ZipFile

# Settings
projectID = 925200
copyFiles = ['world/', 'whitelist.json', 'ops.json', 'eula.txt', 'server.properties' ,'user_jvm_args.txt', 'usercache.json', 'whitelist.json', 'banned-ips.json', 'banned-players.json']
javaVersionRequired = 21
serverLaunch = 'startserver.bat'

def getLatestUpload(id: int, pageSize: int = 1) -> dict:
    url = f"https://www.curseforge.com/api/v1/mods/{id}/files?pageIndex=0&pageSize={pageSize}&sort=dateCreated&sortDescending=true&removeAlphas=true"
    response = urlopen(url) 
    return json.loads(response.read()) 

def getJavaLatestVersions() -> dict:
    url = 'https://java.oraclecloud.com/javaVersions'
    response = urlopen(url)
    return json.loads(response.read())

def getAddionalFiles(id: int, fileId: int) -> dict:
    url = f"https://www.curseforge.com/api/v1/mods/{id}/files/{fileId}/additional-files"
    response = urlopen(url) 
    return json.loads(response.read()) 

def downloadFile(id: int, fileName: str):
    first4 = int(f"{id}"[:4])
    last3 = int(f"{id}"[4:])
    url = f"https://mediafilez.forgecdn.net/files/{first4}/{last3}/{fileName}"
    urlretrieve(url, f"./{fileName}")

def downloadJavaLatest(version: int) -> str:
    file = f"jdk-{version}_windows-x64_bin.zip"
    url = f"https://download.oracle.com/java/{version}/latest/{file}"
    urlretrieve(url, f"./{file}")
    return file
    
def extractFile(fileName: str):
    with ZipFile(fileName, 'r') as zObject:
        zObject.extractall('./')
        
def getFolderName(fileName: str) -> str:
    content = None
    with ZipFile(fileName, 'r') as zObject:
        content = zObject.namelist()
    return content[0]

def remove_readonly(func, path, exc_info):
    "Clear the readonly bit and reattempt the removal"
    # ERROR_ACCESS_DENIED = 5
    if func not in (os.unlink, os.rmdir) or exc_info[1].winerror != 5:
        raise exc_info[1]
    os.chmod(path, stat.S_IWRITE)
    func(path)

def delContent(source: str):
    if os.path.isfile(source):
        os.remove(source)
        
    elif os.path.isdir(source):
        os.chmod(source, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
        shutil.rmtree(source, ignore_errors=False, onerror=remove_readonly)
    
    print(f"Deleted: {source}")

def copyContent(source: str, destination: str):
    delContent(destination)
    
    if os.path.isfile(source):
        shutil.copyfile(source, destination)
    
    elif os.path.isdir(source):
        os.chmod(source, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
        shutil.copytree(source, destination)
        
    print(f"Copied: '{source}' to '{destination}'")

def getFolderUpdateList(latest_folder: str) -> list:
    with os.scandir() as entries:
        dir_list = []
        for dir in [entry.name for entry in entries if entry.is_dir()]:
            if dir != latest_folder[:-1] and 'Server' in dir:
                dir_list += [{'dir': dir, 'version': float(re.match(r".*-(\d?\d\.\d\d)", dir)[1])}]
        dir_list = sorted(dir_list, key=lambda x: (x['version']))
    return dir_list

def getJavaFolderList(latest_folder: str) -> list:
    with os.scandir() as entries:
        dir_list = []
        for dir in [entry.name for entry in entries if entry.is_dir()]:
            if dir != latest_folder and 'jdk' in dir:
                dir_list += [{'dir': dir, 'version': float(re.match(r"jdk-(\d?\d)\.", dir)[1])}]
        dir_list = sorted(dir_list, key=lambda x: (x['version']))
    return dir_list

def startServer(folderName: str):
    os.system(f'{folderName[:-1]}\\{serverLaunch}')
        
def handleUpdate(updateId: int):
    print('Searching Addional Files')
    files = getAddionalFiles(projectID, updateId)
    
    # Retreive file from list
    serverFile = None
    for file in files['data']:
        if 'Server' in file['displayName']:
            serverFile = file
            break
    
    if serverFile:
        fileName: str = serverFile['fileName']
        fileId: int = serverFile['id']
        
        # Download if not exist
        if not os.path.exists(f"./{fileName}"):
            print('Downloading Update')
            downloadFile(fileId, fileName)
        
        # Extract if not exist
        folderName = getFolderName(fileName)
        if not os.path.exists(f"./{folderName}"):
            print('Extracting Update')
            extractFile(fileName)
            
            # Scan current directory and return list without latest version
            dir_list = getFolderUpdateList(folderName)
                
            # If old version exists then copy files to newest version
            if len(dir_list):
                print('Copying Old Data')
                last_version = dir_list.pop()
                for file in copyFiles:
                    copyContent(f"./{last_version['dir']}/{file}", f"./{folderName}{file}")
            
            # Remove all but the latest 2 server versions folders
            for dir in dir_list:
                delContent(dir['dir'])
            
        # Remove all but the latest server version zip archive
        for x in os.listdir():
            if 'Server' in x and x.endswith(".zip") and x != fileName:
                delContent(x)
                
def getLatestUpdateDir() -> str:
    with os.scandir() as entries:
        dir_list = []
        for dir in [entry.name for entry in entries if entry.is_dir()]:
            if 'Server' in dir:
                dir_list += [{'dir': dir, 'version': float(re.match(r".*-(\d?\d\.\d\d)", dir)[1])}]
        dir_list = sorted(dir_list, key=lambda x: (x['version']))
    if dir_list:
        return f"{dir_list.pop()['dir']}/"
    else:
        return None

def checkForUpdates():
    print('Retrieving Updates')
    updates = getLatestUpload(projectID)
    hasServerPack: bool = updates['data'][0]['hasServerPack']
    updateId = updates['data'][0]['id']

    if not hasServerPack:
        updates = getLatestUpload(projectID, 8)
        
        latestUpdate = None
        for update in updates['data']:
            if update['hasServerPack']:
                latestUpdate = update
                break
        
        updateId = latestUpdate['id']

    handleUpdate(updateId)

def handleJavaUpdate() -> str:
    print('Checking for Java JDK updates')
    javaUpdates = getJavaLatestVersions()
    javaLatest: str = None
    for update in javaUpdates['items']:
        if int(update['jdkVersion']) is javaVersionRequired:
            javaLatest = update['latestReleaseVersion']
            break
    
    # Download latest and extract
    if not os.path.exists(f"./jdk-{javaLatest}"):
        print(f"Downloading Java JDK version: {javaLatest}")
        fileName = downloadJavaLatest(javaVersionRequired)
        
        print(f"Extracting Java JDK Version: {javaLatest}")
        extractFile(fileName)
        
    # Remove all but the latest java version folders
    java_dir_list = getJavaFolderList(f"jdk-{javaLatest}")
    for item in java_dir_list:
        delContent(item['dir'])
    
    # Remove all but the latest java version zip archive
    for x in os.listdir():
        if 'jdk' in x and x.endswith(".zip") and x != f"jdk-{javaVersionRequired}_windows-x64_bin.zip":
            delContent(x)
            
    return javaLatest

def checkJava():
    print('Checking Java Version Installed')
    javaVersionStr = os.popen('java --version').read()
    version = int(re.match(r"java\s(\d?\d)\.", javaVersionStr)[1])
    
    if version < javaVersionRequired:
        latest = handleJavaUpdate()
        os.environ['ATM10_JAVA'] = f"{os.path.dirname(os.path.abspath(sys.argv[0])) }/jdk-{latest}/bin/java.exe"
        
def main(args=None):
    checkForUpdates()
    checkJava()
    
    folderName = getLatestUpdateDir()
    if folderName:
        print('Starting Server')
        startServer(folderName)
    else:
        print('Server folder not found!')
    
if __name__ == '__main__':
    main()