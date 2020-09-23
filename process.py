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

    def get_class(self, className):
        self.className = className

    def get_function(self, functionName):
        self.functionName.append(functionName)


def print_diff_info_list(diffInfoList):
    for i in diffInfoList:
        print(i.commit)
        print(i.diff)
        print(i.hashCode1, i.hashCode2)
        s = "\n"
        # print(s.join(i.info))
        print(i.className)
        print(i.functionName)
        print("####################################")


def check_dir(dirName):
    if not os.path.exists(dirName):
        os.makedirs(dirName)


def java_create(path, dirName, name, msg):
    # path = path or r'/tmp/pycharm_project_805/'
    full_path = dirName + "/" + path + "/" + name + '.java'
    check_dir(dirName + "/" + path)
    with open(full_path, "w") as file:
        file.write(msg)


def get_hash_code(commitInfo):
    beforeHashCodeList = []
    afterHashCodeList = []
    log_list = commitInfo.split("\n")
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
                beforeHashCodeList.append(hashCode1)
                afterHashCodeList.append(hashCode2)
    return beforeHashCodeList, afterHashCodeList


def create_java_file(path, hashCodeList, dirName, repo):
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
            java_create(path, dirName, str(i), javaCode)
        i = i + 1


path = r'/mnt/data1/source_code'
fileList = os.listdir(path)
for i in fileList:
    if i.endswith(".py") or i.endswith(".txt"):
        fileList.remove(i)

for k in range(len(fileList)):
    print fileList[k] + " start " + str(k)
    fileName = fileList[k]
    repoPath = path + '/' + fileName
    repo = Repo(repoPath)
    commit_log = repo.git.log('-p', max_count=10)
    log_list = commit_log.split("\n")

    commit_log_list = []
    log_length = len(log_list)
    diffInfoList = []
    dirName = r'/tmp/pycharm_project_136/javaFile'
    i = 0
    tmpInfo = ""
    # print commit_log
    while i < log_length:
        # print "######################### " + str(i)
        info = str(log_list[i])
        if info.startswith("commit") and tmpInfo != "":
            # print tmpInfo
            commit_log_list.append(tmpInfo)
            tmpInfo = ""
        tmpInfo = tmpInfo + info + "\n"
        i = i + 1
    commit_log_list.append(tmpInfo)
    t = 0
    for index in range(len(commit_log_list)):
        commitInfo = commit_log_list[index]
        beforeHashCodeList, afterHashCodeList = get_hash_code(commitInfo)
        pathBefore = fileName + "/commit" + str(t) + "/before"
        pathAfter = fileName + "/commit" + str(t) + "/after"
        print "create start " + fileName + " commit " + str(index)
        if len(beforeHashCodeList) != 0 or len(afterHashCodeList) != 0:
            create_java_file(pathBefore, beforeHashCodeList, dirName, repo)
            create_java_file(pathAfter, afterHashCodeList, dirName, repo)
            t = t + 1
        print "create end " + fileName + " commit " + str(index)
    print fileList[k] + " end " + str(k)
print "ALL END"
