# 本文档用于接收 孙佳 的前端数据，并用于预测判断值

import json
import tensorflow as tf
import numpy as np
from xpath import handleXpath
from context import handleContext
from position import handlePosition


def sigmoid(num):
    return 1/(1+tf.exp(-num))


def loadDataJson(url):
    # 加载文件夹
    data = []
    with open(url, encoding='utf_8_sig') as load_f:
        lines = load_f.readlines()
        #print("+++++++++ lines in loadDataJson", lines)
        for l in lines:
            #print("+++++++++ l in loadDataJson", l)
            data.append(json.loads(l))
    return data


def translate(data):
    # [{
    # 'id': '1',
    # 'mid_dist': 1.6016319802001957,
    # 'nearest_dist': 0.8,
    # 'anceMatchRate': 0.0,
    # 'contMatchRate': 0.0,
    # 'row': -1,
    # },
    # ] (lenth = the num of A for one B)
    data_arr = np.zeros((len(data), 5))
    #print("*************data", data)
    # 赋值
    for i in range(len(data)):
        data_arr[i][0] = data[i]["mid_dist"]
        data_arr[i][1] = data[i]["nearest_dist"]
        data_arr[i][2] = data[i]["anceMatchRate"]
        data_arr[i][3] = data[i]["contMatchRate"]
        data_arr[i][4] = data[i]["row"]
    return data_arr


def handleTestData(listA, listB):
    test = []
    for i in range(len(listB)):
        temp = []
        for j in range(len(listA[i])):
            # t = {
            #     "id": -1,
            #     "mid_dist": -1,
            #     "nearest_dist": -1,
            #     "anceMatchRate": -1,
            #     "contMatchRate": -1,
            #     "row": 0,
            # }
            t = []
            t1, t2, t5 = handlePosition(
                j["position"], i["position"])
            t3 = handleXpath(
                j["xpath"], i["xpath"])
            t4 = handleContext(
                j["context"], i["context"])
            t.append(t1)
            t.append(t2)
            t.append(t3)
            t.append(t4)
            t.append(t5)
            temp.append(t)
        test.append(temp)
    return tf.Variable(test)


def getData(url):
    data = loadDataJson(url)
    #print("------------------type(data) in getData:", len(data))
    #print("------------------data in getData:", data)
    return data["A"], data["B"]


def getWB(url):
    data = loadDataJson(url)
    print("++++++++++++++data in getWB:", data[0])
    return data[0]["w"], data[0]["b"]


def logistic_match(url_data, url_w_b):
    # 输入参数：需要判断数据的地址 & 使用的 w 和 b
    # 输出参数：res=[{A_text=" ", A_id=num, btn= },{},...,{}]
    # 第一步：提取需要处理的数据    data = { A=[A1,A2,...,An], B=[B1,B2,...,Bn] }
    #A, B = getData(url_data)
    A = []
    B = []
    # 第二步：提取需要的 w, b       w=[], b=[]
    w, b = getWB(url_w_b)

    # 第三步：计算每个B对应的每个A的维度值
    # test = np.arr格式 [ [[x11,x12,x13,x14,x15],[x21,x22,x23,x24,x25],...,[xn1,xn2,xn3,xn4,xn5]]  ,..., ]
    test = handleTestData(A, B)
    res = []  # res记录每个B对应的最优匹配的A所需的内容
    for i in range(len(test)):  # 循环每个B
        # 计算每个A对于B的sig()值
        temp_res = []
        for j in range(len(test[i])):
            val = w*(test[i][j].T)+b
            sig = sigmoid(sum(val))
            temp_res.append(sig)
        max_t_res = max(temp_res)
        if max_t_res < 0.75:
            res.append("null")  # 如果认为没有与B匹配的A, 传入“null”
        else:  # 如果认为有与B匹配的A, 传入响应的信息
            max_index = temp_res.index(max(max_t_res))
            res.append({
                "A_text": A[max_index]["context"],
                "btn": False,
                "A_id": A[max_index]["id"],
                "B_xPath": B[i]["xPath"]})

    return res


if __name__ == '__main__':
    # 第一步：获取信息
    logistic_match(
        'dataset/demo_data/nA1B_testData/2021-7-7-NA1B-ALL.txt', 'best_para_w_b.txt')
