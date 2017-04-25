import requests as req
import pandas as pd
import time
import re
import random
import image_OCR
import SqlHelper
import SpiderLog
import traceback




def LocalTime():
	return time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))

#初始化相关数据
def init():
	# proxy_list=SqlHelper.GetProxyList()
	court_list=SqlHelper.GetCourtList()
	df=SqlHelper.cc_data()
	loaddata=df.set_index('Court')
	for x in df['Court']:
		cc_dic[x]=loaddata.ix[x,'TotalCount']
	
	

# 随机获取代理ip
def get_proxy():
	number = random.randint(0, len(proxy_list))
	return proxy_list[number]


def url_get(spider_name):

	# 目标网站地址
	url = 'http://wenshu.court.gov.cn/List/ListContent'
	# 代理列表
	proxy_list = []
	# 法院列表
	court_list = []
	cc_dic={}#初始法院url条数
	# url相关
	courtName_list=[] #法院名称列表
	docID_list=[]     #案件文书ID，即案件url的后缀
	createtime_list=[]#创建时间
	ispull_list=[]#是否已经获取正文的标识
	#正则匹配规则
	count_pattern='"Count":"(\d+)"'
	court_pattern='"法院名称":"(.*?)"'
	DocID_pattern='"文书ID":"(.*?)"'

	# proxy_list=SqlHelper.GetProxyList()
	court_list=SqlHelper.GetCourtList()
	df=SqlHelper.cc_data()
	loaddata=df.set_index('Court')
	for x in df['Court']:
		cc_dic[x]=loaddata.ix[x,'TotalCount']



	print(LocalTime() + str(spider_name) + "------start------")
	SpiderLog.writeIndfoLog(str(spider_name) + "------start------")
	# proxies = {'http': get_proxy()}
	while True:
		for x in court_list:
			try:
				CourtName_DocID=SqlHelper.CourtName_DocID(x)
			except:
				print('数据库连接异常，重新连接')
				continue
			loop_num=0
			CourtInput_count=0
			court_index = 1
			while court_index<101:
				param = {'Param': '法院名称:' + x, 'Index': court_index, 'Page': '20', 'Order': '裁判日期', 'Direction': 'desc'}
				try:
					print(LocalTime() + '爬虫' + str(spider_name) + ':正在获取' + x + ':第' + str(court_index) + '页的内容')
					SpiderLog.writeIndfoLog('yf爬虫' + str(spider_name) + ':正在获取' + x + ':第' + str(court_index) + '页的内容')
					response = req.post(url, data=param, timeout=30)
					result = response.text
					if str(result).find('emind')>0:
						image_OCR.image_ocr('',spider_name)
						response = req.post(url, data=param, timeout=30)
						result = response.text

					text_result=str(result).replace('\\','')
					CountResult=re.findall(count_pattern, text_result)
					CourtResult=re.findall(court_pattern, text_result)
					DocIDResult=re.findall(DocID_pattern, text_result)

					if len(CountResult)>0:
						
						if int(CountResult[0])==int(cc_dic[x]):
							print(LocalTime()+'yf爬虫'+str(spider_name)+':该法院未查到增量数据，跳入爬取下一个法院')
							SpiderLog.writeIndfoLog('yf爬虫'+str(spider_name)+':该法院未查到增量数据，跳入爬取下一个法院')
							break
						else:						
						#获取文书ID
							for k in range(len(DocIDResult)):
								if DocIDResult[k] in CourtName_DocID :
									continue
								else:
									CourtInput_count+=1
									docID_list.append(DocIDResult[k])
									ispull_list.append(0)
									courtName_list.append(CourtResult[k])
									createtime_list.append(LocalTime())
						if len(docID_list)>100:
							df=pd.DataFrame({'CourtName':courtName_list,'DocID':docID_list,'IsPull':ispull_list,'CreateTime':createtime_list})
							SqlHelper.InputUrl(df=df)
							docID_list=[]
							ispull_list=[]
							courtName_list=[]
							createtime_list=[]
							print(LocalTime()+'yf爬虫'+str(spider_name)+'更新url数据成功')
							SpiderLog.writeIndfoLog('yf爬虫'+str(spider_name)+'更新url数据成功')
						#若已经获取到足够的数据就退出查询此法院
						if int(CountResult[0])-int(cc_dic[x])<=CourtInput_count:
							cc_dic[x]=CountResult[0]
							SqlHelper.UdateTotalCount(x, CountResult[0])
							print(LocalTime()+'yf爬虫'+str(spider_name)+'已获取到足够数据，跳入下一个法院')
							break
						else:
							court_index+=1
					else:
						#防止死循环
						loop_num+=1
						if loop_num>3:
							break
				except Exception as e:
					print(traceback.format_exc())
					SpiderLog.writeIndfoLog(traceback.format_exc())
					continue

		print(LocalTime() + str(spider_name) + "------end------")

if __name__ == '__main__':
	url_get('1')