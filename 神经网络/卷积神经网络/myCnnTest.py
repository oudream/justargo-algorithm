#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys

import gParam
import numpy as np
from myCnn import Ccnn
from numpy import *
import struct

sys.path.append('../')
import dataset.mnist as mt

# code
# 卷积层的数目
cLyNum = 10
# 池化层的数目
pLyNum = 10
fLyNum = 50
oLyNum = 10
train_num = 50

def loadImageSet(which=0):
    print "load image set"
    binfile=None
    if which==0:
        binfile = open("/eee/mnist/train-images-idx3-ubyte", 'rb')
    else:
        binfile=  open("/eee/mnist/t10k-images-idx3-ubyte", 'rb')
    buffers = binfile.read()

    head = struct.unpack_from('>IIII' , buffers ,0)
    print "head,",head

    offset=struct.calcsize('>IIII')
    imgNum=head[1]
    width=head[2]
    height=head[3]
    #[60000]*28*28
    bits=imgNum*width*height
    bitsString='>'+str(bits)+'B' #like '>47040000B'

    imgs=struct.unpack_from(bitsString,buffers,offset)

    binfile.close()
    imgs=np.reshape(imgs,[imgNum,width,height])
    print "load imgs finished"
    return imgs

def loadLabelSet(which=0):
    print "load label set"
    binfile=None
    if which==0:
        binfile = open("/eee/mnist/train-labels-idx1-ubyte", 'rb')
    else:
        binfile=  open("/eee/mnist/t10k-labels-idx1-ubyte", 'rb')
    buffers = binfile.read()

    head = struct.unpack_from('>II' , buffers ,0)
    print "head,",head
    imgNum=head[1]

    offset = struct.calcsize('>II')
    numString='>'+str(imgNum)+"B"
    labels= struct.unpack_from(numString , buffers , offset)
    binfile.close()
    labels=np.reshape(labels,[imgNum,1])

    #print labels
    print 'load label finished'
    return labels

myCnn = Ccnn(cLyNum, pLyNum, fLyNum, oLyNum)
# ylabel = mt.loadLabelSet(1)
ylabel = loadLabelSet(1)
# print(len(ylabel))
# exit()

# 循环处理800条数据
for iter0 in range(gParam.MAX_ITER_NUM):
    for i in range(train_num):
        print('iter:', iter0)
        print('----- num:', i)
        # 读取图片数据
        # data = myCnn.read_pic_data(gParam.TOP_PATH, i)
        # data = mt.loadImageSet(1, 2)[i];
        data = loadImageSet(1)[i]
        # print(data.shape)
        # exit()
        # print shape(data)
        ylab = int(ylabel[i])
        # 取得 图片的行数和列数 28行*28列
        d_m, d_n = shape(data)
        # 卷积之后的行数
        m_c = d_m - gParam.C_SIZE + 1
        # 卷积之后的列数
        n_c = d_n - gParam.C_SIZE + 1
        # 池化之后的行数
        m_p = int(m_c / myCnn.pSize)
        # 池化之后的列数
        n_p = int(n_c / myCnn.pSize)
        state_c = zeros((m_c, n_c, myCnn.cLyNum))
        state_p = zeros((m_p, n_p, myCnn.pLyNum))
        for n in range(myCnn.cLyNum):
            # 对输入层进行卷积 20层 每层5行5列
            state_c[:, :, n] = myCnn.convolution(data, myCnn.kernel_c[:, :, n])
            # print shape(myCnn.cLyNum)
            tmp_bias = ones((m_c, n_c)) * myCnn.cLyBias[:, n]
            # 对卷积之后的层 进行激活
            state_c[:, :, n] = np.tanh(state_c[:, :, n] + tmp_bias)  # 加上偏置项然后过激活函数
            # 对激活之后的卷积层 进行池化
            state_p[:, :, n] = myCnn.pooling(state_c[:, :, n], myCnn.pooling_a)
        # 两个返回分别是 1*1*100  12*12*100
        state_f, state_f_pre = myCnn.convolution_f1(state_p, myCnn.kernel_f, myCnn.weight_f)
        # print shape(state_f), shape(state_f_pre)
        # 进入激活函数
        # 1 * 100
        state_fo = zeros((1, myCnn.fLyNum))  # 全连接层经过激活函数的结果
        for n in range(myCnn.fLyNum):
            state_fo[:, n] = np.tanh(state_f[:, :, n] + myCnn.fLyBias[:, n])
        # 进入softmax层
        output = myCnn.softmax_layer(state_fo)
        err = -output[:, ylab]
        # 计算误差
        y_pre = output.argmax(axis=1)
        # print output
        # 计算误差
        # print err
        myCnn.cnn_upweight(err, ylab, data, state_c, state_p, \
                           state_fo, state_f_pre, output)
    # print myCnn.kernel_c
    # print myCnn.cLyBias
    # print myCnn.weight_f
    # print myCnn.kernel_f
    # print myCnn.fLyBias
    # print myCnn.weight_output

# predict
test_num = []
for i in range(10):
    test_num.append(train_num + i + 1)

for i in test_num:
    # data = myCnn.read_pic_data(gParam.TOP_PATH, i)
    # data = mt.loadImageSet(1, 2)[i];
    data = loadImageSet(1)[i]
    # print shape(data)
    ylab = int(ylabel[i])
    d_m, d_n = shape(data)
    m_c = d_m - gParam.C_SIZE + 1
    n_c = d_n - gParam.C_SIZE + 1
    m_p = m_c / myCnn.pSize
    n_p = n_c / myCnn.pSize
    state_c = zeros((m_c, n_c, myCnn.cLyNum))
    state_p = zeros((m_p, n_p, myCnn.pLyNum))
    for n in range(myCnn.cLyNum):
        state_c[:, :, n] = myCnn.convolution(data, myCnn.kernel_c[:, :, n])
        # print shape(myCnn.cLyNum)
        tmp_bias = ones((m_c, n_c)) * myCnn.cLyBias[:, n]
        state_c[:, :, n] = np.tanh(state_c[:, :, n] + tmp_bias)  # 加上偏置项然后过激活函数
        state_p[:, :, n] = myCnn.pooling(state_c[:, :, n], myCnn.pooling_a)
    state_f, state_f_pre = myCnn.convolution_f1(state_p, myCnn.kernel_f, myCnn.weight_f)
    # print shape(state_f), shape(state_f_pre)
    # 进入激活函数
    state_fo = zeros((1, myCnn.fLyNum))  # 全连接层经过激活函数的结果
    for n in range(myCnn.fLyNum):
        state_fo[:, n] = np.tanh(state_f[:, :, n] + myCnn.fLyBias[:, n])
    # 进入softmax层
    output = myCnn.softmax_layer(state_fo)
    # 计算误差
    y_pre = output.argmax(axis=1)
    print('真实数字为%d', ylab, '预测数字是%d', y_pre)
