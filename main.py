#coding:utf-8
'''
读取hst文件
'''

import struct
import time       
import datetime
import hstutils
import json
import requests
import threading
import logging
import initEnvironment 
import winUtils

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


# SERVER_IP = "125.77.254.10"
# SERVER_PORT="1014"

# http://125.77.254.10:1014/
# http_price = "http://127.0.0.1:9080/test"
# http_history = "http://127.0.0.1:9080/history"
http_price = "http://125.77.254.10:1014/test"
http_history = "http://125.77.254.10:1014/history"
hst_file_path ="../history/default/"

"""
获取当前价格
"""
def getPriceNow(symbol_names):
    url = http_price
    datas={
        "symbol_names":symbol_names
        }
    r = requests.get(url,datas)
    data = json.loads(r.text)
    price = data['price']
    price = float(price)
    return price
"""
获取当前价格(测试接口,该接口数据都是模拟数据)
"""
def getPriceNow_Test():
    url = http_price
    r = requests.get(url)
    data = json.loads(r.text)
    price = data['price']
    price = float(price)
    return price

"""
获取中间的历史数据
"""
def getHistory(symbol_names,period,point):
    url = http_history
    datas={
        "symbol":symbol_names,
        "period":period
        }
    r = requests.get(url,datas)
    data = json.loads(r.text)
    
    plist = []
    for dt in data:
        times = dt['date']
        open = dt['open']
        high = dt['high']
        low = dt['low']
        close = dt['close']
        volume = dt['volume']
    
        times = long(times)
        open = hstutils.floatHandle(open,point)
        high = hstutils.floatHandle(high,point)
        low = hstutils.floatHandle(low,point)
        close = hstutils.floatHandle(close,point)
        volume = long(volume)
        
        priceStruc = hstutils.PriceStruct(times, open, high, low, close,volume)
        plist.append(priceStruc)
    return plist


"""
用测试数据接口更新当前图表
"""
def updateChartTest(filename):
    logging.info("正在更新文件 %s", filename )
    priceStruc = hstutils.PriceStruct(0, 0.0, 0.0, 0.0, 0.0,0)
    while 1:
        headunit = hstutils.readHstHead(filename)
    #     读取时间间隔,并转换成秒
        space = headunit.period[0] * 60
    #     保留小数点位数
        point  = headunit.point
    #     读取前两个unit
        previous = hstutils.redHstBackwards(filename,1)# 前一个
        the_first_two = hstutils.redHstBackwards(filename,2)# 前两个
        # 核对时间
        
        previous_time = int(float(previous.times))
        the_first_two_time = int(float(the_first_two.times))
        # 获取价格 
        price_now = getPriceNow_Test()
        logging.info("获取价格 %s",price_now)
        # 设置时间
        ostime = time.time()
        priceStruc.times = int(ostime)
        # print "时间差 previous_time ",(previous_time - the_first_two_time),"space",space
        if (previous_time - the_first_two_time) >= space:
            # print "新增一个"
            # 新增一个
            priceStruc.opens = price_now
            priceStruc.high = price_now
            priceStruc.low = price_now
            priceStruc.close =price_now
            priceStruc.vols = 1000
            hstutils.writeStruct(filename, priceStruc)
        else:
            # print "正在更新当前"
            #更新当前
            if(price_now > priceStruc.high):
                priceStruc.high = price_now
            if(price_now<priceStruc.low):
                priceStruc.low = price_now
            priceStruc.close = price_now
            hstutils.updateStruct(filename, priceStruc)
        winUtils.updateCharts()
        # print "当前价格:",price_now
        time.sleep(1)


"""
更新当前图表
"""
def updateChart(filename,symbol_names):
    print "正在更新文件"+filename
    priceStruc = hstutils.PriceStruct(0, 0.0, 0.0, 0.0, 0.0,0)
    while 1:
        headunit = hstutils.readHstHead(filename)
    #     读取时间间隔,并转换成秒
        space = headunit.period[0] * 60
    #     保留小数点位数
        point  = headunit.point
    #     读取前两个unit
        previous = hstutils.redHstBackwards(filename,1)# 前一个
        the_first_two = hstutils.redHstBackwards(filename,2)# 前两个
        # 核对时间
        
        previous_time = int(float(previous.times))
        the_first_two_time = int(float(the_first_two.times))
        # 获取价格 
        price_now = getPriceNow(symbol_names)
        # 设置时间
        ostime = time.time()
        priceStruc.times = int(ostime)
        print "时间差 previous_time ",(previous_time - the_first_two_time),"space",space
        if (previous_time - the_first_two_time) >= space:
            print "新增一个"
            # 新增一个
            priceStruc.opens = price_now
            priceStruc.high = price_now
            priceStruc.low = price_now
            priceStruc.close =price_now
            priceStruc.vols = 1000
            hstutils.writeStruct(filename, priceStruc)
        else:
            print "正在更新当前"
            #更新当前
            if(price_now > priceStruc.high):
                priceStruc.high = price_now
            if(price_now<priceStruc.low):
                priceStruc.low = price_now
            priceStruc.close = price_now
            hstutils.updateStruct(filename, priceStruc)
        print "当前价格:",price_now
        time.sleep(1)


"""
开始运行某个周期的图表
"""
def startChartRun(symbol,period):
    symbol_names = symbol
    filename = hst_file_path+symbol_names+str(period)+".hst"
    point = 2;
    # 写入头部
    hstutils.writeHstHead(filename,symbol_names,period,point)
    # 写入一个时间段的历史数据
 
    plist = getHistory(symbol,period,point)
    hstutils.writeStructList(filename,plist);
    # 更新图表
#     updateChart(filename,symbol)
    updateChartTest(filename)
    # 刷新MT4界面
    # winUtils.updateCharts()
    
"""
启动一个图表数据的实时线程
"""
def startThread():
    while symbolList:
#         try:
        code = symbolList.pop()
#         startChartRun(symbol,period)
        s = "\r code:"+code+"\r"
        periodList = [5,15,30]
        period = 0
        for p in periodList:
            period = p
            startChartRun(code,period)
#         except Exception as exp:
#             print "error code:",code,"period",period,"exp:",exp
#             continue
        

if __name__ == '__main__':
# 初始化raw文件
    initEnvironment.initFunc()
#     股票代码列表
    symbolList = []
    with open("marketInfo.json") as json_file:
        json_data = json.load(json_file)
        for i,data in enumerate(json_data):
             symboljson = data["symbols"]
             for symbol in symboljson:
                 coreId = str(symbol["coreId"])
                 symbolList.append(coreId)
        
    threads = []
# 启动线程数量100
    for i in range(100):
        t = threading.Thread(target=startThread)
        t.setName(i)
        threads.append(t)
    for t in threads:
        t.start()
    for t in threads:
        t.join()
