# coding=utf-8

#导入模板模块
from flask import render_template
from app import app

@app.route('/')

@app.route('/index')
def index():
	return render_template('index.html')

'''
'''

import sys
sys.path.append(r"C:/Users/Administrator/Documents/duplicateChecking/Flask/app/web_mod")
import web_mod

@app.route('/upload', methods=['GET', 'POST'])
def upload():	# 用户上传文件时，根据 ID 或时间生成用户个人文件夹，用于保存论文和查重结果。用户可单独访问个人网址，相当于登陆功能
    web_mod.upload_file()
    # web_mod.create_result(uid='user_123')
    # 上传文件后就应该开始比对了，这里应该传参 paper_file_name，执行 
    return render_template('upload.html')

'''
'''

sys.path.append(r"C:/Users/Administrator/Documents/duplicateChecking/Flask/app/dupl_ckg")
import dupl_ckg

@app.route('/result')
def result():
    # dupl_ckg.debug_import()  # 测试 dupl_ckg 模块是否导入
    # dupl_ckg.result_sim(paper_file_name='')  # 计算单篇论文与数据库相似度
	# dupl_ckg.result_details(paper_a='', paper_b='')  # 计算两篇论文相似度及详情
    # return render_template('userid.html', userid=, )  # 为每个用户生成结果页（尚未完成）
    uid = '0010'  # 为用户生成唯一 uid
    content = web_mod.read_file()
    return render_template('result.html', uid=uid, content=content)
    
@app.route('/init')
def init():
    dupl_ckg.db_build()
    return render_template('index.html')

@app.route('/test')
def test():
    # dupl_ckg.result_sim(paper_file_name='')
    result_temp = mdb.details.find().sort([('hammingDis',-1)])
    result_details = []
    for i in result_temp:
        result_details.append([i['parag_a'], i['parag_b']])
    return render_template('result.html', uid='0001', result_details=result_details)

@app.route('/test/result_all')
def test_result_all():
    dupl_ckg.result_all(paper_name='', hamming_dis_threshold=3)
    return render_template('test.html', func_name='result_all')
    
@app.route('/test/generate')
def test_generate():
    content = web_mod.generate(uid='')
    return render_template('result.html', uid='1', content=content)
    # return render_template('test.html', func_name='generate')
    
@app.route('/test/read')
def test_read():
    content = web_mod.read_file()
    return render_template('result.html', uid='0010', content=content)

@app.route('/test/time')
def test_time():
    clock_0 = time()
    # s1 = '0001001001001000000100100100100000010010010010000001001001001000'
    # s2 = '1000010000100001100001000010000110000100001000011000010000100001'
    s1 = '0010001000100010'
    s2 = '0010001000100011'
    for i in range(1,10000000):
        # dupl_ckg.hammingDis(s1, s2)
        if s1 == s2:
            return s1
    clock_1 = time()
    print('success! time = ', clock_1-clock_0)
    return render_template('test.html', func_name='time')

'''
测试 pymongo
'''

sys.path.append(r"C:/Users/Administrator/Documents/duplicateChecking/Flask/app/flk_mdb")
import flk_mdb
import pymongo
from flask import request, redirect, url_for
from flk_mdb import Todo
from time import time

mongo = pymongo.MongoClient('127.0.0.1', 27017)
mdb = mongo.test

@app.route('/test/create_index')
def test_create_index():
    mdb.all.create_index([("name", pymongo.TEXT)])
    # mdb.all.create_index([("name", pymongo.ASCENDING)])
    return render_template('test.html', func_name='create_index')

@app.route('/test/get_index')
def test_get_index():
    # mdb.all.get_index()
    return render_template('test.html', func_name='get_index')

@app.route('/todo/',methods=['GET'])
def mdb_index():
    todosss = mdb.list.find({})
    return  render_template('mdb_index.html',todos=todosss)

@app.route('/todo/', methods=['POST'])
def mdb_add():
    content = request.form.get('content', None)
    if not content:
        abort(400)
    mdb.list.insert(Todo.create_doc(content))
    return redirect('/todo/')

@app.route('/todo/<content>/finished')
def mdb_finish(content):
    result = mdb.list.update_one(
        {'content':content}, 
        {'$set': {
            'is_finished': True,
            'finished_at': time()
            }
        }
    )
    return redirect('/todo/')

@app.route('/todo/<content>')
def mdb_delete(content):
    result = mdb.list.delete_one(
        {'content':content}
    )
    return redirect('/todo/')

''' Flask + Vue 测试 '''

@app.route('/todovue')
def index_todovue():
    return render_template('formdata_vue.html')
