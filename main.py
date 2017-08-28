#coding:utf-8
'''
读取hst文件
'''

import struct
import time       
import datetime
import hstutils
import json
import threading
import logging
import initEnvironment 
import tushare as ts
import pandas as pd 
import traceback
import requests as rq


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



hst_file_path ="../history/default/"
filepath = ""


start_date = "20000101"



"""
获取历史数据
"""
def getHistory(symbol,period,point):
    plist = []
    if symbol == ""  or symbol is None:
        logging.info( "wrongful  symbol")
        return plist
    try:
        # 日线数据从临时数据获取
        if period == 1440:
            coreId = str(symbol)
            start = start_date
            end_date = datetime.datetime.now().strftime('%Y%m%d')
            file_path = "ephemeral.data/"+coreId+".csv"

            market = "0"
            # print coreId
            if coreId[0] != "6":
                market = "1"
            url = "http://quotes.money.163.com/service/chddata.html?code="+market+coreId+"&start="+start+"&end="+end_date
            r = rq.get(url)
            with open(file_path , 'wb') as f:
                f.write(r.content)
                f.close()
            df = pd.read_csv(file_path,encoding="gbk",skiprows =1,names=["datetime","coreId","name","close","high","low","opens","before_close","Fluctuation","Chg","Turnover_rate","volume","amount","TotleMarket","CirculationMarket","volnum"])
            df = df.iloc[::-1]
            
            for unit in df.iterrows():
                dataformate = "%Y-%m-%d"
                dates = unit[1]['datetime']
                d=datetime.datetime.strptime(dates,dataformate)
                times=int(time.mktime(d.timetuple()))
                opens = unit[1]['opens']
                close = unit[1]['close']
                high = unit[1]['high']
                low = unit[1]['low']
                volume = unit[1]['volume']
                
                times = long(times)
                opens = hstutils.floatHandle(opens,point)
                high = hstutils.floatHandle(high,point)
                low = hstutils.floatHandle(low,point)
                close = hstutils.floatHandle(close,point)
                volume = long(volume)
                
                priceStruc = hstutils.PriceStruct(times, opens, high, low, close,volume)
                plist.append(priceStruc)
            return plist
        else:
            # 分钟数据从tushare获取
            period = str(period)
            # print "get_k_data",symbol,period
            data = ts.get_k_data(symbol,ktype=period)
            # print "=========",symbol,":",period
            if data is None:
                print "tushare is no data symbol %s period %s",symbol,period
                return plist
            resultlist = []
            lens = len(data)
            for unit in data.iterrows():
                dates = unit[1]['date']
        #             长度等于10的是%Y-%m-%d格式,16的是%Y-%m-%d %H:%M 格式
                dataformate = "%Y-%m-%d %H:%M"
                date_len = len(dates)
                if date_len == 10 :
                    dataformate = "%Y-%m-%d"
                d=datetime.datetime.strptime(dates,dataformate)
                times=int(time.mktime(d.timetuple()))
                opens=unit[1]['open']
                close=unit[1]['close']
                high=unit[1]['high']
                low=unit[1]['low']
                volume=unit[1]['volume']
                
                times = long(times)
                opens = hstutils.floatHandle(opens,point)
                high = hstutils.floatHandle(high,point)
                low = hstutils.floatHandle(low,point)
                close = hstutils.floatHandle(close,point)
                volume = long(volume)
                
                priceStruc = hstutils.PriceStruct(times, opens, high, low, close,volume)
                plist.append(priceStruc)
            return plist
    except Exception,e:
        print 'str(Exception):\t', str(Exception)
        print 'str(e):\t\t', str(e)
        print 'repr(e):\t', repr(e)
        print 'e.message:\t', e.message
        print 'traceback.print_exc():'
        traceback.print_exc()
        print 'traceback.format_exc():\n%s' % traceback.format_exc()
        errormsg = "method get_k_data [ symbol %s period %s ]",symbol,period
        logging.info(errormsg)
        return []
    



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
    if plist is not None:
        hstutils.writeStructList(filename,plist);

    
"""
启动一个图表数据的实时线程
"""


def startThread():
    while symbolList:
        code = symbolList.pop()
        periodList = [5,15,30,60,1440]
        for period in periodList:
            t = threading.Thread(target=startChartRun,args=(code,period))
            t.start()
if __name__ == '__main__':
    print "environment init start ...................................."
#     初始化raw文件,并返回所有股票代码
    symbolList = initEnvironment.initFunc()

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

    print "over .........................close window and open MT4"