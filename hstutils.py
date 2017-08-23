# -*- coding: UTF-8 -*-
'''
Created on 2017年5月24日

@author: songy
'''

import struct
import requests
import json
import logging

#基础版本
VERSION = 401
# 公司名称
C_COPYRIGHT = "(C)opyright 2003, MetaQuotes Software Corp."
# 货币对名称
CURRENCY = "SYTEST"
#  周期 (单位分钟) 
PERIOD = 240
 #小数点位数
DECIMAL_SIZE = 5
 #基准报时时间
STANDARD_TIME = 1302790985
#同步时间
SYNC_TIME = 0
#将来应用字节数
FUTURE_UNIT = 13


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename='log/iceblaze.log',
                    filemode='w')
# 配置控制台打印
# 设置控制台日志打印格式
formatter = logging.Formatter('%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')
console = logging.StreamHandler()
console.setFormatter(formatter)
console.setLevel(logging.DEBUG)
logging.getLogger('').addHandler(console)


        
"""
头文件数据结构
"""
class HeadStruct(object):
    version = None
    company =  None
    currency =  None
    period =  None
    point =  None
    basetime =  None
    synctime =  None
    future =  None
    
    def __init__(self):
        pass
"""
一个数据单元的结构
"""
class PriceStruct(object):
    """docstring for ClassName"""
    def __init__(self, times, opens, high, low, close,vols):
        self.times = times
        self.opens = opens
        self.high = high
        self.low = low
        self.close = close
        self.vols = vols



"""写入头文件
@symbol 货币名称 string
@period  周期 int
@point 小数点位数 int
"""
def writeHstHead(fileName,symbol,period,point):
    content = struct.pack("i", VERSION)
    content += struct.pack("64s", C_COPYRIGHT)
    content += struct.pack("12s", symbol)
    content += struct.pack("i", period)
    content += struct.pack("i", point)
    content += struct.pack("l", STANDARD_TIME)
    content += struct.pack("l", SYNC_TIME)
# 未来应用
    content += '\x00'*FUTURE_UNIT*4

    with open(fileName, 'wb') as fp:
        fp.write(content)
        


"""
保留小数字
"""
def floatHandle(num,point):
    num = float(num)
    num = ('%.{}f'.format(point))%num
    num = float(num)
    return num


"""
保留N位小数
"""

"""
解析倒数N个unit数据 返回PriceStruct
"""
def redHstBackwards(filename,n):
    with open(filename, 'rb') as fp:
        content = fp.read()
    tip = len(content)-60*n
    cTime = content[tip:tip+4]
    cOpen = content[tip+8:tip+16]
    cHigh = content[tip+16:tip+24]
    cLow = content[tip+24:tip+32]
    cClose = content[tip+32:tip+40]
    cVol = content[tip+40:tip+44]
    
   
    times = struct.unpack("l", cTime)[0]
    
    opens = struct.unpack("d", cOpen)[0]
    high = struct.unpack("d", cHigh)[0]
    low = struct.unpack("d", cLow)[0]
    close = struct.unpack("d", cClose)[0]
    vol = struct.unpack("l", cVol)[0]
    p = PriceStruct(times, opens, high, low, close,vol);
#     print "time:",struct.unpack("l", cTime)
# 
#     print "open:",struct.unpack("d", cOpen)
# 
#     print "high:",struct.unpack("d", cHigh)
# 
#     print "low:",struct.unpack("d", cLow)
# 
#     print "close:",struct.unpack("d", cClose)
# 
#     print "vol:",struct.unpack("l", cVol)
    return p

"""
 读取hst文件头部返回headStruct
"""
def readHstHead(filename):
    
    
    with open(filename, 'rb') as fp:
    
        content = fp.read()
    
#     report = "";
    # 读取头文件结构信息
    
    headunit = HeadStruct()
    # 基础版本
    _version = struct.unpack("i", content[0:4])
    headunit.version = _version
#     print _version
    
    # 公司版本信息
    _company = "".join(struct.unpack("64c", content[4:68]))
    headunit.company=_company
#     print _company
    
    # 货币对名称
    _currency = "".join(struct.unpack("12c", content[68:80]))
    headunit.currency = _currency
#     print "_currency:",_currency
    
    # 周期 (单位分钟)
    _period = struct.unpack("i", content[80:84])
    headunit.period = _period
#     print "周期",_period
    
    # 小数点位数
    _point = struct.unpack("i", content[84:88])
    headunit.point = _point
#     print _point
    
    # 基准报时
    _basetime = struct.unpack("l", content[88:92])
#     print _basetime
    
    # 同步时间
    _synctime = struct.unpack("l", content[92:96])
#     print _synctime
    
    # 将来应用
    _future = struct.unpack("13i", content[96:148])
#     print _future
    
    return headunit
    # 循环结构
#     report +="基础版本:"+str(_version)+"\r\n"
#     report +="公司版本信息:"+str(_company)+"\r\n"
#     report +="货币对名称:"+str(_currency)+"\r\n"
#     report +="周期:"+str(_period)+"\r\n"
#     report +="小数点位数:"+str(_point)+"\r\n"
#     report +="基准报时:"+str(_basetime)+"\r\n"
#     report +="同步时间:"+str(_synctime)+"\r\n"
#     report +="将来应用:"+str(_future)+"\r\n"
#     
#     
#     content_len = len(content)
#     index = 0;
#     for tip in range(148,content_len,60):
#         cTime = content[tip:tip+4]
#         cOpen = content[tip+8:tip+16]
#         cHigh = content[tip+16:tip+24]
#         cLow = content[tip+24:tip+32]
#         cClose = content[tip+32:tip+40]
#         cVol = content[tip+40:tip+44]
#     
#         print "time:",struct.unpack("l", cTime)
#     
#         print "open:",struct.unpack("d", cOpen)
#     
#         print "high:",struct.unpack("d", cHigh)
#     
#         print "low:",struct.unpack("d", cLow)
#     
#         print "close:",struct.unpack("d", cClose)
#     
#         print "vol:",struct.unpack("l", cVol)
        # report += str([str(cTime),str(cOpen),str(cHigh),str(cLow),str(cClose)])
        
        
"""
删除一个结构体，并写入一个新的
@filename 文件名
"""
def updateStruct(filename,pstruct):
    
    content = struct.pack("l", pstruct.times)
    content += '\x00'*4
    content += struct.pack("d", pstruct.opens)
    content += struct.pack("d", pstruct.high)
    content += struct.pack("d", pstruct.low)
    content += struct.pack("d", pstruct.close)  
    content += struct.pack("l", pstruct.vols)
    # 全部写完要隔开16个 \x00    
    content += '\x00'*16

    logging.info("updateStruct() filename %s ",filename)
    with open(filename, 'rb+') as fp:
        # 从文件末尾，移动一个结构体,然后写入一个结构体
        fp.seek(-60,2)
        fp.write(content)
        fp.close()
        
"""
写入PriceStruct[]列表
"""
def writeStructList(fileName,structlist):
    content = ""
    for pstruct in structlist:
        # timeArray = time.localtime(t)
        # otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
        # print "writingdata...     time:",otherStyleTime," opens:", pstruct.opens,"high",pstruct.high," low:",pstruct.low," close:" , pstruct.close
        content += struct.pack("l", pstruct.times)
        content += '\x00'*4
        content += struct.pack("d", pstruct.opens)
        content += struct.pack("d", pstruct.high)
        content += struct.pack("d", pstruct.low)
        content += struct.pack("d", pstruct.close)  
        content += struct.pack("l", pstruct.vols)
        # 全部写完要隔开16个 \x00    
        content += '\x00'*16
    with open(fileName, 'ab') as fp:
        fp.write(content) 

"""
追加写入单个结构体
"""        
def writeStruct(filename,pstruct):
    content = "";
    content += struct.pack("l", pstruct.times)
    content += '\x00'*4
    content += struct.pack("d", pstruct.opens)
    content += struct.pack("d", pstruct.high)
    content += struct.pack("d", pstruct.low)
    content += struct.pack("d", pstruct.close)  
    content += struct.pack("l", pstruct.vols)
    # 全部写完要隔开16个 \x00    
    content += '\x00'*16
    with open(filename, 'ab') as fp:
        fp.write(content) 
       
"""
从网络获取一个价格单位
获取一个pstruct
"""
def getPriceStruct():
    r = requests.get(url='http://125.77.254.10:1014/')
    data = json.loads(r.text)
    times = data['timestamp']
    opens = data['open']
    high = data['high']
    low = data['low']
    close = data['close']
    vol = data['vol']
    p = PriceStruct(times, opens, high, low, close,vol)
    return p

