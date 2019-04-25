# coding=utf-8

'''
    准备工作
'''

import codecs
import numpy as np
import jieba
import jieba.analyse
import os
import sys
sys.path.append(r"C:/Users/Administrator/Documents/duplicateChecking/Flask/app/flk_mdb")
from flk_mdb import *
import pymongo
import time

mongo = pymongo.MongoClient('127.0.0.1', 27017)
# mdb = mongo.test
mdb = mongo.test

db_data = []
db_hash = []
db_doc_idx = {}

def hammingDis(simhash1, simhash2):  # 计算汉明距离
    t1 = '0b' + simhash1
    t2 = '0b' + simhash2
    n = int(t1, 2) ^ int(t2, 2)
    i = 0
    while n:
        n &= (n-1)
        i += 1
    # print("hammingDis() executed!")
    return i

def string_hash(source):
    if source == '':
        return 0
    else:
        x = ord(source[0]) << 7
        m = 1000003
        mask = 2 ** 128 - 1
        for c in source:
            x = ((x * m) ^ ord(c)) & mask
        x ^= len(source)
        if x == -1:
            x = -2
        x = bin(x).replace('0b', '').zfill(64)[-64:]
    # print("string_hash() executed!")
    return str(x)
    
def simhash(content):
    # clock_0 = time.time()  # 测试时间
    # seg = jieba.cut(content)  # 分词
    # file_tmp = open(r'C:\Users\Administrator\Documents\duplicateChecking\Flask\app\dupl_ckg\simhash_time.txt', 'a')
    # clock_1 = time.time()
    # print(content, '\nt1: ', clock_1-clock_0, file=file_tmp)
    jieba.analyse.set_stop_words('./app/dupl_ckg/stopwords.txt')  # 去除停用词
    # clock_2 = time.time()
    # print('t2: ', clock_2-clock_1, file=file_tmp)
    keyWord = jieba.analyse.extract_tags(
        # '|'.join(seg), topK=20, withWeight=True, allowPOS=())  # 根据 TD-IDF 提取关键词，并按照权重排序
        content, topK=20, withWeight=True, allowPOS=())
    # file_tmp = open(r'C:/Users/Administrator/Documents/duplicateChecking/Flask/app/dupl_ckg/testenter.txt', 'a'))
    # print('=len(keyWord): ', len(keyWord), '==content: ', content, '==keyWord: ', keyWord, '=', file=file_tmp)
    # file_tmp.close()
    if len(keyWord) < 6:
        return ''  # 少于5个词放弃这个句子
    # clock_3 = time.time()
    # print('t3: ', clock_3-clock_2, file=file_tmp)
    keyList = []
    # strKeyWord = ''
    for feature, weight in keyWord:  # 对关键词进行 hash
        # strKeyWord += str(feature) + ':' + str(weight) + ' '
        weight = int(weight * 20)
        # file_tmp = open(r'C:\Users\Administrator\Documents\duplicateChecking\Flask\app\dupl_ckg\simhash_strKeyWord.txt', 'a')
        # print('【feature: ', feature, '】', file = file_tmp)
        feature = string_hash(feature)      
        temp = []
        for i in feature:
            if(i == '1'):
                temp.append(weight)
            else:
                temp.append(-weight)
        # print(temp)
        keyList.append(temp)
        # print('【hash: ', feature, '】', file = file_tmp)  # 打印测试
        # file_tmp.close()
    # clock_4 = time.time()
    # print('t4: ', clock_4-clock_3, file=file_tmp)
    list1 = np.sum(np.array(keyList), axis=0)
    if(keyList == []):  # 编码读不出来
        # return strKeyWord, '00'
        return '00'
    simhash = ''
    for i in list1:  # 权值转换成 hash 值
        if(i > 0):
            simhash = simhash + '1'
        else:
            simhash = simhash + '0'
    # print("simhash() executed!")
    # clock_5 = time.time()
    # print('t5: ', clock_5-clock_4, '\nstrKeyWord: ', strKeyWord, '\nsimhash: ', simhash, '\n\n', file=file_tmp)
    # file_tmp.close()
    # return strKeyWord, simhash
    return simhash

    
'''
    建立数据库
'''
    
def db_build():
    clock_0 = time.time()
    print("db_build() starting …")
    prepath = './docs'
    doc_name = os.listdir(prepath)
    # global db_data, db_hash  # 全局变量
    # db_data = []
    # db_hash = []
    # doc_name_idx = []
    # count = 0
    for name in doc_name:
        # file_tmp = open(r'C:\Users\Administrator\Documents\duplicateChecking\Flask\app\dupl_ckg\simhash_time.txt', 'a')
        # clock_0 = time.time()
        # print(count, '\t', name)
        # count += 1
        mdb.idx.insert(Paper.create_idx(name))
        # doc_name_idx.append(name)
        txt = np.loadtxt(codecs.open(os.path.join(prepath, name), encoding=u'gb18030',errors='ignore')
                        , dtype=np.str, delimiter="\r\n", encoding='gb18030')
        # txt = np.char.replace(txt, '\u3000', '')  # 去掉全角空格和制表符
        # txt = np.char.replace(txt, '\t', '')
        for paragraph in txt:
            paragraph = paragraph.replace('\u3000', '').replace('\t', '').replace('  ', '').replace('\r', ' ')  # 去除全角空格和制表符，换行替换为空格
            # file_tmp = open(r'C:/Users/Administrator/Documents/duplicateChecking/Flask/app/dupl_ckg/paragraph.txt', 'a', encoding='gb18030')
            # print('【paragragh: ', paragraph, '】', file=file_tmp)
            # if paragraph == '' or paragraph == ' ' or paragraph[0].isdigit():
            if paragraph == '' or paragraph == ' ':
                continue
            # strKeyWord, shash = simhash(paragraph)
            shash = simhash(paragraph)
            # if strKeyWord == '':
                # continue
            if shash == '':
                continue
            # db_data.append([name, paragraph, strKeyWord]) 
            # db_data.append([name, paragraph])
            # db_data.append([count, paragraph])
            # db_hash.append(shash)
            # print('【hash: ', shash, '】', file=file_tmp)
            # file_tmp.close()
            # mdb.test0.insert(Paper.create_mdb(name, paragraph, strKeyWord, shash))  # 保存到 MongoDB
            mdb.all.insert(Paper.create_mdb(name, paragraph, shash))
        # clock_1 = time.time()
        # print(name, '\n【T】: ', clock_1-clock_0, '\n', file=file_tmp)
    print("db_build() executed!")
    clock_1 = time.time()
    print('【time_build: ', clock_1-clock_0, '】')
'''
    存储数据库至本地，以便之后使用
'''
def db_save():
    print("db_save() starting …")
    global db_data, db_hash  # 全局变量
    db_data = np.array(db_data)
    db_hash = np.array(db_hash)
    np.save("./app/dupl_ckg/db_data.npy", db_data)
    np.save("./app/dupl_ckg/db_hash.npy", db_hash)
    print("db_save() executed!")

'''
    论文查重 - 准备工作
'''

from collections import OrderedDict
import numpy as np

def get_db_doc_idx(db_data):
    # print("get_db_doc_idx() starting …")

    # doc_name_idx = []
    # doc_name = os.listdir('./docs')
    # count = 0
    # for name in doc_name:
    #     doc_name_idx.append(name)
    #     count += 1

    global db_doc_idx  # 全局变量
    db_doc_idx = {}  # 初始化 db_doc_idx
    for i in range(len(db_data)): 
        arr = db_data[i]
        # print(' / ', arr, ' / ')  # 打印测试
        # file_tmp = open(r'C:/Users/Administrator/Documents/duplicateChecking/Flask/app/dupl_ckg/get_db_doc_idx.txt', 'a')
        # print('【arr: ', arr, '】【[i]: ', [i], '】【i: ', i, '】', file=file_tmp)
        # file_tmp.close()
        if arr[0] not in db_doc_idx.keys():
            db_doc_idx[arr[0]] = [i]
        else:
            db_doc_idx[arr[0]].append(i)
    # print("get_db_doc_idx() executed!")
    # print(db_doc_idx, '\n')
    return db_doc_idx

# 单篇与数据库相似度
def get_sim(paper_name, hamming_dis_threshold):
    print("get_sim() starting …")

    paper_name = '烟花爆竹流向监控平台的设计与实施-第4次修改（隆重1).txt'
    a_name = paper_name
    TEMP_name_idx = []
    name_idx = mdb.idx.find({"name":{"$ne":a_name}})
    Paper.save_to_array(TEMP_name_idx, name_idx, 'name')  # 保存结果
    # for i in name_idx:
        # TEMP_name_idx.append(i["name"])
    # for i in name_idx:
        # TEMP_name_idx.append(i["name"])
    # for i in TEMP_name_idx:
    #     print(i)
    for b_name in TEMP_name_idx:
        sim_count = 0
        item_a = item_b = []
        TEMP_a_parag = TEMP_a_shash = []
        a_parag = mdb.all.find({"name":a_name})
        Paper.save_to_array(TEMP_a_parag, a_parag, 'paragraph')  # 保存结果
        Paper.save_to_array(TEMP_a_shash, a_parag, 'shash')
        # for i in a_parag:
            # TEMP_a_parag.append(PAPER_TEMP(i["paragraph"], i["shash"]))
        counter_a = counter_b = 0
        for a_idx in TEMP_a_parag:
            TEMP_b_parag = TEMP_b_shash = []
            b_parag = mdb.all.find({"name":b_name})
            Paper.save_to_array(TEMP_b_parag, b_parag, 'paragraph')  # 保存结果
            Paper.save_to_array(TEMP_b_shash, b_parag, 'shash')
            counter_a += 1
            # for i in b_parag:
                # TEMP_b_parag.append(PAPER_TEMP(i["paragraph"], i["shash"]))
            for b_idx in TEMP_b_parag:
                print('【', TEMP_a_shash[counter_a], '】【', TEMP_b_shash[counter_b], '】')
                # item_result = hammingDis(TEMP_a_shash[counter_a], TEMP_b_shash[counter_b])
                # item_result = hammingDis(TEMP_a_parag.shash, TEMP_b_parag.shash)
                counter_b += 1
                # if item_result < hamming_dis_threshold:
                    # sim_count += 1
                    # item_a.append(TEMP_a_parag[counter_a])
                    # item_b.append(TEMP_b_parag[counter_b])
                    # item.append([a_idx.paragraph, b_idx.paragraph])
                    # print('【item: ', item, '】【item_er')
        print('【', b_name, '】【', sim_count, '】')
        if sim_count > 9:
            for parag_a, parag_b in item:
                # print(parag_a, '//', parag_b)
                mdb.dupl_parag_details.insert(Paper.create_dupl_parag_details(a_idx.name, parag_a, b_idx.name, parag_b))
            mdb.dupl_parag_sum.insert(Paper.create_dupl_parag_sum(a_idx.name, b_idx.name, sim_count))
                # result_dict[b_name["name"]] = sim_count
    dupl_sum = mdb.dupl_parag_sum.find().sort([("KEY",-1)])
    for i in dupl_sum:
        print('【', i["name_b"], '】【', i["dupl_with_b"], '】')
    print("get_sim() executed!")

def get_sim_bak(paper_name, db_doc_idx, db_hash, hamming_dis_threshold=5):
    print("get_sim() starting …")

    doc_name = os.listdir('./docs')
    result_dict = {}

    for b_key in db_doc_idx.keys():
        if a_key == b_key:
            continue
        sim_count = 0
        for a_idx in db_doc_idx[a_key]:
            item = []
            for b_idx in db_doc_idx[b_key]:
                item_result = hammingDis(db_hash[a_idx], db_hash[b_idx])
                if item_result <= hamming_dis_threshold:
                    item.append([a_idx, b_idx])
            # print('\na_key: ', a_key, '\nb_key: ', b_key, '\ndb_doc_idx[a_key]: ', db_doc_idx[a_key], '\ndb_doc_idx[b_key]: ', db_doc_idx[b_key])
            if len(item) > 0:
                sim_count += len(item)
            # print('\na_idx: ', a_idx, '\titem: ', item, '\tsim_count: ', sim_count)
        if sim_count > 5:  # 只保存重复超过5句的文章
            result_dict[b_key] = sim_count
    
    result_dict = OrderedDict(sorted(result_dict.items(), key=lambda t: t[1], reverse=True))

    print("get_sim() executed!")
    return result_dict


# 两篇相似情况
def get_sim_details(paper_name_a, paper_name_b,  
                    db_doc_idx, db_hash, db_data, hamming_dis_threshold=5,
                    print_details='short'):
    # print("get_sim_details() starting …")
    a_key = paper_name_a
    b_key = paper_name_b
    result_dict = {}
    for a_idx in db_doc_idx[a_key]:
        for b_idx in db_doc_idx[b_key]:
            item_sim = hammingDis(db_hash[a_idx], db_hash[b_idx])
            if item_sim <= hamming_dis_threshold:
                if item_sim not in result_dict.keys():
                    result_dict[item_sim] = []
                result_dict[item_sim].append([db_data[a_idx], db_data[b_idx]])
    
    result_dict = OrderedDict(sorted(result_dict.items()))
    

    # print("get_sim_details() executed!")
    return result_dict

'''
    论文查重 - 加载本地数据库
'''
def db_load():
    print("db_load() starting …")
    global db_data, db_hash  # 全局变量
    db_data = np.load(r'C:/Users/Administrator/Documents/duplicateChecking/Flask/app/dupl_ckg/db_data.npy')
    db_hash = np.load(r'C:/Users/Administrator/Documents/duplicateChecking/Flask/app/dupl_ckg/db_hash.npy')
    print("db_load() executed!")

'''
    计算单篇论文与数据库中论文的相似度
    # 仅得数存在相似关系的论文的相关数据，值越大，越相似
'''
def result_sim(paper_name, GENERATE_PATH, target_file):
    print("result_sim() starting …")
    
    global db_doc_idx # 全局变量
    db_doc_idx = get_db_doc_idx(db_data)
    paper_name = '科协学会专家数据库的设计与实施-第4次修改（降重）.txt'
    result_dict = get_sim(paper_name, db_doc_idx, db_hash, hamming_dis_threshold=5)
    
    full_path = GENERATE_PATH + '\\' + target_file
    file = open(full_path, 'a')
    
    for k,v in result_dict.items():
        print(k, v, file=file)
        
    file.close()
    
    print("result_sim() executed!")
    return result_dict

'''
    输出并打印两篇论文的相似情况
    # hamming distance 越小，越相似
'''
def result_details(paper_name_a, paper_name_b, GENERATE_PATH, target_file):
    print("result_details() starting …")
    
    global db_doc_idx  # 全局变量
    db_doc_idx = get_db_doc_idx(db_data)
    # print('\ndb_doc_idx: \n', db_doc_idx, '\n')  # 打印测试
    result_dict_details = get_sim_details(paper_name_a, paper_name_b, db_doc_idx, db_hash, db_data, hamming_dis_threshold=6)
    
    full_path = GENERATE_PATH + '\\' + target_file
    file = open(full_path, 'a')
    
    print('paper a:', paper_name_a, '\npaper b:', paper_name_b, '\n', file=file)  # 打印标题
    for k in result_dict_details.keys():
        print('hamming distance:', str(k), file=file)
        for a, b in result_dict_details[k]:
            print('-'*100, file=file)
            print('\ta:\t', a[1], file=file)
            print('\tb:\t', b[1], file=file)
        print('', file=file)
        
    file = file.close()
    
    print("result_details() executed!")


'''
    按相似度排序，打印相似段落
'''

def result_all(paper_name, GENERATE_PATH, target_file_name):
    print("result_details() starting …")
    
    # doc_name_idx = []
    # doc_name = os.listdir('./docs')
    # count = 1
    # for name in doc_name:
    #     doc_name_idx[count] = name
    #     count += 1

    paper_name = '科协学会专家数据库的设计与实施-第4次修改（降重）.txt'
    result_dict = result_sim(paper_name, GENERATE_PATH, target_file_name) 
    full_path = GENERATE_PATH + '\\' + target_file_name
    
    counter = 1
    for paper_name_counter, hamming_dis in result_dict.items():
        target_file = open(full_path, 'a')
        print('■'*100,'\n', file=target_file)
        print('【No.%d】:'%counter, paper_name_counter, '\n', file=target_file)
        target_file = target_file.close()  # 写入 all 部分后需要关闭文件，否则写入顺序会出错
        
        result_details(paper_name, paper_name_counter, GENERATE_PATH, target_file_name)
        counter += 1
        
    target_file = open(full_path, 'r')
    content = target_file.readlines()
    target_file.close()
    
    print("result_details() executed!")
    return content
    
'''
    初始化数据库
'''

def init():
    print("init() starting …")
    # db_build()  # 仅在论文库更新时再次 db_build() 和 db_save() 即可
    # db_save()
    # db_load()
    print("init() executed!")