import os
import sys
from git import Repo

reload(sys)
sys.setdefaultencoding('utf-8')


class DiffInfo:
    def __init__(self, commit, diff, index, info):
        self.commit = commit
        self.diff = diff
        self.hashCode1 = index[6:13]
        self.hashCode2 = index[15:22]
        self.info = info
        self.functionName = []
        self.className = ""

    def getClass(self, className):
        self.className = className

    def getFunction(self, functionName):
        self.functionName.append(functionName)


def printDiffInfoList(diffInfoList):
    for i in diffInfoList:
        print(i.commit)
        print(i.diff)
        print(i.hashCode1, i.hashCode2)
        s = "\n"
        # print(s.join(i.info))
        print(i.className)
        print(i.functionName)
        print("####################################")


def checkDir(dirName):
    if not os.path.exists(dirName):
        os.makedirs(dirName)


def java_create(index, path, name, msg):
    # path = path or r'/tmp/pycharm_project_805/'
    full_path = path + "/" + index + "/" + name + '.java'
    checkDir(path + "/" + index)
    file = open(full_path, 'w')
    file.write(msg)


def create_java_file(index, hashCodeList, dirName, repo):
    # for i in range(len(hashCodeList)):
    #     javaCode = repo.git.cat_file('-p', hashCodeList[i])
    #     java_create(index, dirName, i, javaCode)
    i = 0
    for hashCode in hashCodeList:
        try:
            javaCode = repo.git.cat_file('-p', hashCode)
        except:
            print(fileList[k])
            print(hashCode)
        else:
            java_create(index, dirName, str(i), javaCode)
        i = i + 1


path = r'/mnt/data1/source_code'
fileList = os.listdir(path)
for i in fileList:
    if i.endswith(".py") or i.endswith(".txt"):
        fileList.remove(i)
print fileList[21]
for k in range(len(fileList)):
    # for k in range(1):
    fileName = fileList[k]
    repoPath = path + '/' + fileName
    repo = Repo(repoPath)
    beforeHashCode = []
    afterHashCode = []
    commit_log = repo.git.log('-p', max_count=10)
    log_list = commit_log.split("\n")
    commit_log_list = []
    log_length = len(log_list)
    i = 0
    tmpInfo = ""
    diffInfoList = []
    dirName = r'/tmp/pycharm_project_805/javaFile'

    # while i < log_length:
    #     info = str(log_list[i])
    #     if info.startswith("commit") and tmpInfo != "":
    #         commit_log_list.append(tmpInfo)
    #         tmpInfo = ""
    #     tmpInfo = tmpInfo + info + "\n"
    #     i = i + 1
    for i in range(len(log_list)):
        thisInfo = str(log_list[i])
        if thisInfo.startswith("diff") and thisInfo.endswith("java"):
            nextInfo = str(log_list[i + 1])
            if nextInfo.startswith("index"):
                index1 = nextInfo.index(" ")
                index2 = nextInfo.index("..")
                hashCode1 = nextInfo[index1 + 1:index2]
                nextInfo = nextInfo[index2 + 2:]
                index3 = nextInfo.index(" ")
                hashCode2 = nextInfo[:index3]
                # print hashCode1
                # print hashCode2
                # print hashCode1
                beforeHashCode.append(hashCode1)
                afterHashCode.append(hashCode2)

    pathBefore = str(k) + "/before"
    pathAfter = str(k) + "/after"
    print("create start " + fileName)
    create_java_file(pathBefore, beforeHashCode, dirName, repo)
    create_java_file(pathAfter, afterHashCode, dirName, repo)
    print("create end " + fileName)
