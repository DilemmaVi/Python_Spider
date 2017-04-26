import requests as req
import pandas as pd
import re
import time
import SqlHelper
import image_OCR
import traceback


def LocalTime():
	return time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))

def get_count():

	courtList=SqlHelper.GetCourtList()
	url='http://wenshu.court.gov.cn/List/ListContent'
	proxyHost = "proxy.abuyun.com"
	proxyPort = "9020"
	# 代理隧道验证信息
	proxyUser = "H1GX6CNSSW177N7D"
	proxyPass = "B5F2CBAE62C4BDB9"
	proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
	  "host" : proxyHost,
	  "port" : proxyPort,
	  "user" : proxyUser,
	  "pass" : proxyPass,
	}
	proxies = {
	    "http"  : proxyMeta,
	    "https" : proxyMeta,
	}



	for x in courtList:
		try:
			CountResult=''
			data={'Param':'法院名称:' +x, 'Index': '1','Page':'5','Order':'裁判日期','Direction':'desc'}
			r=req.post(url,data = data,proxies=proxies)
			if str(r.text).find('emind')>0:
				image_OCR.image_ocr('',1)
				r=req.post(url,data = data)
			response=str(r.text).replace('\\','')
			count_pattern='"Count":"(\d+)"'
			CountResult=re.findall(count_pattern, response)
			if CountResult!='':
				SqlHelper.UdateTotalCount(x, CountResult[0])
			print('正在获取'+x+'的数据,总共发现有:'+CountResult[0])
		except Exception as e:
			print(traceback.format_exc())

if __name__ == '__main__':
	get_count()