import os
import pickle


class Node:
    def __init__(self, functionName, nodeName):
        self.functionName = functionName
        self.nodeName = nodeName
        self.index = -1
        self.content = ''

    def init_index(self, index):
        self.index = index

    def get_content(self, content):
        self.content = content


def get_function_content(javaList, className, functionName):
    upper = 0
    lower = 0
    for i in range(len(javaList)):
        line = javaList[i]
        if ("class " + className) in line:
            upper = i
            left = 0
            right = 0
            for j in range(i + 1, len(javaList)):
                lineTmp = javaList[j].replace(" ", "")
                if lineTmp == "{":
                    left = left + 1
                if lineTmp == "}":
                    right = right + 1
                if left == right:
                    lower = j
                    break
            break
    if lower == 0:
        return ""
    classContent = javaList[upper:lower + 1]
    upper2 = 0
    lower2 = 0
    for i in range(len(classContent)):
        line = classContent[i].strip()
        line = line.strip()
        if (functionName in line) and (
                line.startswith('public') or line.startswith('private') or line.startswith('protected')):
            upper2 = i
            left = 0
            right = 0
            for j in range(i + 1, len(classContent)):
                lineTmp = classContent[j].replace(" ", "")
                if lineTmp == "{":
                    left = left + 1
                if lineTmp == "}":
                    right = right + 1
                if left == right:
                    lower2 = j
                    break
            break
    if lower2 == 0:
        return ""
    functionContentList = classContent[upper2:lower2 + 1]
    functionContent = ""
    b = functionContentList[0].strip()
    diff = len(functionContentList[0]) - len(b)
    for i in functionContentList:
        i = i[diff:]
        functionContent = functionContent + "\n" + i
    return functionContent[1:]


with open(r"D:\USE\coding\try\pythonProject1\process\test\commit0\beforeNodeList.data", "r") as file:
    nodeList = pickle.load(file)

path = r'D:\USE\coding\try\pythonProject1\downloadNow\before'
javaFileList = os.listdir(path)
for index in range(len(nodeList)):
    node = nodeList[index]
    node.get_content("")
    nodeFunctionNameList = node.functionName.split(".")
    nodeFunctionName = nodeFunctionNameList[-1]
    nodeClassName = nodeFunctionNameList[-2]
    for javaFile in javaFileList:
        javaFilePath = path + '/' + javaFile
        with open(javaFilePath, 'r') as file:
            java = file.read()
            javaList = java.split("\n")
        functionContent = get_function_content(javaList, nodeClassName, nodeFunctionName)
        if functionContent != "":
            node.get_content(functionContent)
            nodeList[index] = node
for i in nodeList:
    print i.functionName
    print i.content
