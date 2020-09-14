#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import paramiko
import os
from stat import S_ISDIR as isdir
import numpy as np

reload(sys)
sys.setdefaultencoding('utf-8')


class Node:
    def __init__(self, content, name):
        self.content = content
        self.name = name
        self.index = 0

    def initIndex(self, index):
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


def download(remote_dir_before, remote_dir_after, local_dir_before, local_dir_after):
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


def cmdDoxygen(index):
    os.system("doxygen D:\doxygen\Doxyfile" + index)


def dic2list(dic):
    r = []
    for i in dic:
        r.append(i)
    for i in dic:
        r[i] = dic[i]
    return r


def save_by_np(index, dicList):
    dir = r"adjacencyMatrixDicList"
    for i in range(len(dicList)):
        path = dir + "/" + str(i)
        check_local_dir(path)
        ad = dic2list(dicList[i])
        res = np.array(ad)
        np.save(path + r"/" + index, res)


nodeListBeforeList = []
nodeListAfterList = []
# nodeDic = {}
# nodeContentDic = {}
adjacencyMatrixDicBeforeList = []
adjacencyMatrixDicAfterList = []
print("start")
for i in range(1):
    nodeList = []
    nodeDic = {}
    nodeContentDic = {}
    adjacencyMatrixDic = {}
    remote_dir_before = '/tmp/pycharm_project_805/javaTest/' + str(i) + '/before'
    remote_dir_after = '/tmp/pycharm_project_805/javaTest/' + str(i) + '/after'
    # 本地文件存放路径（绝对路径或者相对路径都可以）
    local_dir_before = 'downloadNow/before'
    local_dir_after = 'downloadNow/after'
    print("download start #######################")
    download(remote_dir_before, remote_dir_after, local_dir_before, local_dir_after)
    print("download end #######################")

    print("cmd before start #######################")
    cmdDoxygen("Before")
    print("cmd before end ######################")

    print("draw before start")
    path = "D:\\doxygen\\doxygen\\workspace\\html"
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
                        tmpNode.initIndex(len(nodeList))
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
    nodeListBeforeList.append(nodeList)
    adjacencyMatrixDicBeforeList.append(adjacencyMatrixDic)
    print("draw before end")

    nodeList = []
    nodeDic = {}
    nodeContentDic = {}
    adjacencyMatrixDic = {}
    print("cmd after start #######################")
    cmdDoxygen("After")
    print("cmd after end ######################")

    print("draw after start")
    path = "D:\\doxygen\\doxygen\\workspace\\html"
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
                        tmpNode.initIndex(len(nodeList))
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
    nodeListAfterList.append(nodeList)
    adjacencyMatrixDicAfterList.append(adjacencyMatrixDic)
    print("draw after end ")
# print(adjacencyMatrixDic)

print "save start"
save_by_np("before", adjacencyMatrixDicBeforeList)
save_by_np("after", adjacencyMatrixDicAfterList)
print "save end"
