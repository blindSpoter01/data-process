#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pickle
import sys
import paramiko
import os
from stat import S_ISDIR as isdir
import numpy as np

reload(sys)
sys.setdefaultencoding('utf-8')


class Node:
    def __init__(self, functionName, nodeName):
        self.functionName = functionName
        self.nodeName = nodeName
        self.index = -1

    def init_index(self, index):
        self.index = index


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


def cmd_doxygen(index):
    os.system("doxygen E:\pythonProject\dataProcess\Doxyfile" + index)


def draw():
    nodeContentDic = {}
    nodeList = []
    nodeDic = {}
    adjacencyMatrixDic = {}
    path = "D:/doxygen/workspace/html"
    filesList = os.listdir(path)
    for file in filesList:
        if not file.endswith("cgraph.dot") or not file.endswith("icgraph.dot"):
            continue
        fileName = path + "\\" + file
        with open(fileName) as f:
            dot_graph = f.read()
            dotGrapgList = dot_graph.split("\n")
        for s in dotGrapgList:
            s = s.strip()
            if s.startswith("Node"):
                if "label=\"" in s:
                    index1 = s.index("label=\"")
                    index2 = s.index(",")
                    content = s[index1 + 7:index2 - 1].replace("\\l", "")
                    nameIndex = s.index(" ")
                    name = s[:nameIndex]
                    if content not in nodeContentDic:
                        tmpNode = Node(content, name)
                        tmpNode.init_index(len(nodeList))
                        nodeList.append(tmpNode)
                        nodeDic[name] = tmpNode
                        nodeContentDic[content] = tmpNode
                    else:
                        nodeDic[name] = nodeContentDic[content]
        for s in dotGrapgList:
            s = s.strip()
            if "->" in s:
                sList = s.split(" ")
                nodeFirst = sList[0]
                nodeSecond = sList[2]
                if not nodeDic[nodeFirst].index in adjacencyMatrixDic:
                    adjacencyMatrixDic[nodeDic[nodeFirst].index] = []
                if "dir=\"back\"" in s:
                    if not nodeDic[nodeSecond].index in adjacencyMatrixDic:
                        adjacencyMatrixDic[nodeDic[nodeSecond].index] = []
                    if nodeDic[nodeFirst].index not in adjacencyMatrixDic[nodeDic[nodeSecond].index]:
                        adjacencyMatrixDic[nodeDic[nodeSecond].index].append(nodeDic[nodeFirst].index)
                else:
                    if nodeDic[nodeSecond].index not in adjacencyMatrixDic[nodeDic[nodeFirst].index]:
                        adjacencyMatrixDic[nodeDic[nodeFirst].index].append(nodeDic[nodeSecond].index)
    return nodeList, adjacencyMatrixDic


def save(nodeList, adjacencyMatrixDic, projectName, index, beforeOrAfter):
    abpath = 'E:/pythonProject/dataProcess/process/' + projectName + '/commit' + str(index) + '/'
    check_local_dir(abpath)
    nodeListFilePath = abpath + '/' + beforeOrAfter + 'NodeList' + '.data'
    adjacencyMatrixDicFilePath = abpath + '/' + beforeOrAfter + 'AdjacencyMatrixDic' + '.data'
    with open(nodeListFilePath, 'wb') as file:
        pickle.dump(nodeList, file)
    with open(adjacencyMatrixDicFilePath, 'wb') as file:
        pickle.dump(adjacencyMatrixDic, file)


with open('project_name_dic.data', 'r') as file:
    project_name_dic = pickle.load(file)
# project_name_dic = {"openstack-infra_gerrit": 1}
for projectName in project_name_dic:
    projectCommitNum = project_name_dic[projectName]
    for i in range(projectCommitNum):
        print "download start #######################"
        remote_dir_before = '/tmp/pycharm_project_136/javaFile/' + projectName + '/commit' + str(i) + '/before'
        remote_dir_after = '/tmp/pycharm_project_136/javaFile/' + projectName + '/commit' + str(i) + '/after'
        # remote_dir_before = '/tmp/pycharm_project_136/javaFile/' + projectName + '/commit5' + '/before'
        # remote_dir_after = '/tmp/pycharm_project_136/javaFile/' + projectName + '/commit5' + '/after'
        local_dir_before = 'downloadNow/before'
        local_dir_after = 'downloadNow/after'
        download_java_file(remote_dir_before, remote_dir_after, local_dir_before, local_dir_after)
        print "download end #######################"

        print "cmd before start #######################"
        cmd_doxygen("Before")
        print "cmd before end ######################"

        print "draw before start ######################"
        nodeList, adjacencyMatrixDic = draw()
        print "draw before start ######################"

        print "save before start ######################"
        save(nodeList, adjacencyMatrixDic, projectName, i, "before")
        print "save before end ######################"

        print "cmd after start #######################"
        cmd_doxygen("After")
        print "cmd after end ######################"

        print "draw after start ######################"
        nodeList, adjacencyMatrixDic = draw()
        print "draw after start ######################"

        print "save after start ######################"
        save(nodeList, adjacencyMatrixDic, projectName, i, "after")
        print "save after end ######################"
