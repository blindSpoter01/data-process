#!/usr/bin/env python
# -*- coding: utf-8 -*-
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


def down_from_remote(sftp_obj, remote_dir_name, local_dir_name):
    """远程下载文件"""
    try:
        remote_file = sftp_obj.stat(remote_dir_name)
    except:
        print remote_dir_name + " not exist"
    else:
        if isdir(remote_file.st_mode):
            # 文件夹，不能直接下载，需要继续循环
            check_local_dir(local_dir_name)
            print('开始下载文件夹：' + remote_dir_name)
            for remote_file_name in sftp_obj.listdir(remote_dir_name):
                sub_remote = os.path.join(remote_dir_name, remote_file_name)
                # print(sub_remote)
                if str(sub_remote).startswith("/tmp") and str(sub_remote).endswith(".java"):
                    sub_remote = sub_remote.replace('\\', '/')
                    sub_local = os.path.join(local_dir_name, remote_file_name)
                    sub_local = sub_local.replace('\\', '/')
                    down_from_remote(sftp_obj, sub_remote, sub_local)
        else:
            # 文件，直接下载
            print('开始下载文件：' + remote_dir_name)
            sftp_obj.get(remote_dir_name, local_dir_name)


def check_local_dir(local_dir_name):
    """本地文件夹是否存在，不存在则创建"""
    if not os.path.exists(local_dir_name):
        os.makedirs(local_dir_name)


def download_java_file(remote_dir_before, remote_dir_after, local_dir_before, local_dir_after):
    # 服务器连接信息
    host_name = '114.212.87.13'
    user_name = 'csy'
    password = 'csy'
    port = 22
    # 远程文件路径（需要绝对路径）
    # remote_dir_before = '/tmp/pycharm_project_805/testjava/before'
    # remote_dir_after = '/tmp/pycharm_project_805/testjava/after'
    # 本地文件存放路径（绝对路径或者相对路径都可以）
    # local_dir_before = 'download2/before/'
    # local_dir_after = 'download2/after/'
    # 连接远程服务器
    t = paramiko.Transport((host_name, port))
    t.connect(username=user_name, password=password)
    sftp = paramiko.SFTPClient.from_transport(t)

    # 远程文件开始下载
    down_from_remote(sftp, remote_dir_before, local_dir_before)
    down_from_remote(sftp, remote_dir_after, local_dir_after)
    # 关闭连接
    t.close()


def get_content(nodeList, javaFileList, path):
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


# 把字典扒下来
with open("project_dict.data", "r") as file:
    project_dict = pickle.load(file)
datasetPath = ""
for project in project_dict:
    commmitTimes = project_dict[project]
    for index in range(len(commmitTimes)):
        # 下载文件

        beforePath = datasetPath + "/" + project + "/commit" + str(index) + "/beforeNodeList.data"
        with open(beforePath, "r") as file:
            beforeNodeList = pickle.load(file)

        beforeJavaFilePath = "commit0/before"
        beforeJaveFileList = os.listdir(beforeJavaFilePath)
        get_content(beforeNodeList, beforeJaveFileList, beforeJavaFilePath)
        with open(beforePath, "w") as file:
            pickle.dump(beforeJaveFileList, file)

        afterPath = datasetPath + "/" + project + "/commit" + str(index) + "/afterNodeList.data"
        with open(afterPath, "r") as file:
            afterNodeList = pickle.load(file)
        afterJavaFilePath = "commit0/before"
        afterJaveFileList = os.listdir(afterJavaFilePath)
        get_content(afterNodeList, afterJaveFileList, afterJavaFilePath)
        with open(afterPath, "w") as file:
            pickle.dump(afterJaveFileList, file)

# with open(r"D:\USE\coding\try\pythonProject1\process\test\commit0\beforeNodeList.data", "r") as file:
#     nodeList = pickle.load(file)
#
# path = r'D:\USE\coding\try\pythonProject1\downloadNow\before'
# javaFileList = os.listdir(path)
# for index in range(len(nodeList)):
#     node = nodeList[index]
#     node.get_content("")
#     nodeFunctionNameList = node.functionName.split(".")
#     nodeFunctionName = nodeFunctionNameList[-1]
#     nodeClassName = nodeFunctionNameList[-2]
#     for javaFile in javaFileList:
#         javaFilePath = path + '/' + javaFile
#         with open(javaFilePath, 'r') as file:
#             java = file.read()
#             javaList = java.split("\n")
#         functionContent = get_function_content(javaList, nodeClassName, nodeFunctionName)
#         if functionContent != "":
#             node.get_content(functionContent)
#             nodeList[index] = node
# for i in nodeList:
#     print i.functionName
#     print i.content
