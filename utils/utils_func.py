# -*- coding: UTF-8 -*-


'''
函数 工具包
'''
import re
from urllib.parse import urlparse
#解析库
from lxml import etree
from hashlib import sha1


#-------- htmlText转化成dom------

def responseTodom(response):
    '''把响应返回的str，解析为HTML dom模式'''
    responseDom = etree.HTML(response.content)
    return responseDom

#------- 字符串，返回哈希值=------


def get_hash(string):
    # str就是unicode了.Python3中的str对应2中的Unicode
    string_encode = string.encode("utf-8")
    s1 = sha1()
    s1.update(string_encode)
    return s1.hexdigest()

#-----------从url 获取域名------


topHostPostfix = (
    '.com','.la','.io','.co','.info','.net','.org','.me','.mobi','.edu.cn',
    '.us','.biz','.xxx','.ca','.co.jp','.com.cn','.net.cn',
    '.org.cn','.mx','.tv','.ws','.ag','.com.ag','.net.ag',
    '.org.ag','.am','.asia','.at','.be','.com.br','.net.br',
    '.bz','.com.bz','.net.bz','.cc','.com.co','.net.co',
    '.nom.co','.de','.es','.com.es','.nom.es','.org.es',
    '.eu','.fm','.fr','.gs','.in','.co.in','.firm.in','.gen.in',
    '.ind.in','.net.in','.org.in','.it','.jobs','.jp','.ms',
    '.com.mx','.nl','.nu','.co.nz','.net.nz','.org.nz',
    '.se','.tc','.tk','.tw','.com.tw','.idv.tw','.org.tw',
    '.hk','.co.uk','.me.uk','.org.uk','.vg', ".com.hk")
regx = r'[^\.]+('+'|'.join([h.replace('.',r'\.') for h in topHostPostfix])+')$'
pattern = re.compile(regx,re.IGNORECASE)

def getDomain(url):
    parts = urlparse(url)
    host = parts.netloc
    m = pattern.search(host)
    res =  m.group() if m else host
    res = res.replace('www.', '')
    if res:
        return res
    else:
        return None



#---- 匹配ip---
def match_ip(string):
    if re.findall(r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b", string):
        return True
    else:return False

