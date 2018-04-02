from flask import Flask,request,render_template, g

from instances.db import MysqlClient,RedisClient
from utils.setting import API_HOST,API_PORT,DATABASES_REDIS,TESTURL,GETTER_ENABLED
import threading
import json,time


__all__ = ['app']

app = Flask(__name__)



SAVE_MSG = None
DOWN_MSG = None
TEST_MSG = None
IPPOOL_MSG = None



def get_conn():
    if not hasattr(g, 'mysql'):
        g.mysql = MysqlClient('proxy')
    return g.mysql


@app.route('/')
def index():

    redis = RedisClient(DATABASES_REDIS['REDIS_SET_KEY'])
    mysql = MysqlClient('proxy')
    context={
        'getterStatus':GETTER_ENABLED,

        'saveThreadMsg':SAVE_MSG,
        'downThreadsMsg':DOWN_MSG,

        'mysqlcount':mysql.getCount(),
        'rediscount':redis.getCount(),
        'testurl':TESTURL,

    }
    return render_template("index.html",**context)



@app.route('/getcount')
def get_count():
    """
    Get the count of proxies
    :return: 代理池总量
    """
    conn = get_conn()
    return str(conn.getCount())


@app.route('/getproxies')
def get_proxy():
    """
    Get a proxy
    :return: count数量的代理
    """
    count = request.args.get('count')
    conn = get_conn()
    proxies= conn.getProxies(int(count))
    content=''
    for proxy in proxies:
        content += proxy[0]+"<br>"
    return content



@app.route('/getrandom')
def get_random():
    """
    随机获取一个proxy
    """
    conn = get_conn()
    proxy= conn.getRandom()
    content = proxy[0]
    return content



@app.route('/getall')
def get_all():
    """
    Get the count of proxies
    :return: 所有代理
    """
    conn = get_conn()
    proxies= conn.getAll()
    content=''
    for proxy in proxies:
        content += proxy[0]+"<br>"
    return content


@app.route('/del')
def delete():
    """
    Get the count of proxies
    :return: 删除代理
    """
    proxy = request.args.get('proxy')
    conn = get_conn()
    return conn.delete(str(proxy))



@app.route('/getwork')
def getWork():
    '''负责采集器里面，保存线程/下载线程的工作状况'''
    global SAVE_MSG,DOWN_MSG

    msg = {
        "downmsg":DOWN_MSG,

        "savemsg":SAVE_MSG,
    }
    msg = json.dumps(msg,ensure_ascii=False)
    return msg



@app.route('/testwork')
def testWork():
    '''负责测试器里面的工作状况'''
    global TEST_MSG

    msg = {
        "restip_count":TEST_MSG,
    }
    msg = json.dumps(msg,ensure_ascii=False)
    return msg


@app.route('/ippool')
def ippool():
    '''负责测试器里面的工作状况'''
    global IPPOOL_MSG
    msg = {
        "faildip_count":IPPOOL_MSG,
    }
    msg = json.dumps(msg,ensure_ascii=False)
    return msg


def processMsg(q_save,q_down):
    '''专门开一个线程，来处理别的线程传过来的数据(保存线程的数据)'''
    global SAVE_MSG,DOWN_MSG,TEST_MSG,IPPOOL_MSG

    redis = RedisClient(DATABASES_REDIS['REDIS_SET_KEY'])
    mysql = MysqlClient('proxy')
    while True:

        try:
            SAVE_MSG = q_save.get(False)
            DOWN_MSG = q_down.get(False)
        except:
            SAVE_MSG = '没有存储线程'
            DOWN_MSG = '没有下载线程'

        try:
            TEST_MSG = redis.getCount()
            IPPOOL_MSG = mysql.getCount()
        except:
            pass


def run(q_save,q_down):
    t = threading.Thread(target=processMsg,args=(q_save,q_down), name='信息处理线程')
    t.setDaemon(True)
    t.start()

    app.run(host=API_HOST, port=API_PORT, debug=True)


if __name__ == '__main__':

    pass
    #run()








