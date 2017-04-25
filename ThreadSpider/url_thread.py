# -*- coding: utf-8 -*-
import requests as req
import pandas as pd
import time
import re
import json
import math
import image_OCR
import SqlHelper
import SpiderLog
import traceback
import random
import demjson



def LocalTime():
	return time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))

def get_url(CourtList,threadlock,spider_num):
	global ProxyList
	print (LocalTime()+':yf爬虫'+str(spider_num)+'正在启动...')
	#SpiderLog.writeIndfoLog('yf爬虫'+str(spider_num)+'正在启动...')
	while True:
		try:
			threadlock.acquire()
			ProxyList=SqlHelper.GetProxyList()
			threadlock.release()

			print(LocalTime()+'yf爬虫'+str(spider_num)+':本次总共需要爬取'+str(len(CourtList))+'个法院的案件链接')
			#SpiderLog.writeIndfoLog('yf爬虫'+str(spider_num)+':本次总共需要爬取'+str(len(CourtList))+'个法院的案件链接')
			# NOdata=[]
			DocID=[]
			CourtName=[]
			IsPull=[]
			CreateTime=[]
			url='http://wenshu.court.gov.cn/List/ListContent'
		except Exception as e:
			print(LocalTime()+traceback.format_exc())
			continue
		for x in CourtList: 
			try:
				threadlock.acquire()
				CourtName_DocID=SqlHelper.CourtName_DocID(x)
				threadlock.release()
				print (LocalTime()+'yf爬虫'+str(spider_num)+':正在获取'+x+'的内容')
				#SpiderLog.writeIndfoLog('yf爬虫'+str(spider_num)+':正在获取'+x+'的内容')
				#这是页数、程序休息时间的定义和三个空的列表用来装筛选后的数据。
				Index=1
				CounrtNum=0#判断是否已经更新完了当前法院的全部数据
				SleepNum= 3
				count=100
				flag=False
				CountData=False
				IsUpdateCourt=''
				threadlock.acquire()
				TotalCount=int(SqlHelper.CourtName_TotalCount(x))
				OnlineCount=0
				threadlock.release()
			except Exception as e:
				print(LocalTime()+'yf爬虫'+str(spider_num)+traceback.format_exc())
				continue			
			while Index <=count:
				# rdint=random.randint(0,len(ProxyList))
				# proxyIP=ProxyList[rdint]
				# proxies={'http':proxyIP}#构造的代理ip
				OcrFlag=True
				my_headers={'User-Agent':'Mozilla/5.0(Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.95Safari/537.36 Core/1.50.1280.400',
             'Accept':'*/*','Accept-Encoding':'gzip, deflate','Accept-Language':'zh-CN,zh;q=0.8','Connection':'keep-alive',
             'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8','X-Requested-With':'XMLHttpRequest'}
				#这一行是搜索条件，根据浏览器post内容得到，通过法院名称和页码来爬取所需链接
				data={'Param':'法院名称:' +x, 'Index': Index,'Page':'20','Order':'裁判日期','Direction':'desc'}			
				try:
					#将网址、请求头、搜索条件等数据上传并取得内容
					r=req.post(url,headers=my_headers, data = data)
					#用 json解码取得的网页内容
				except Exception as e:
					print(LocalTime()+'yf爬虫'+str(spider_num))
					print(str(traceback.format_exc()))
					#SpiderLog.writeErrorLog(traceback.format_exc())
					if str(traceback.format_exc()).find('TimeoutError')>0:
						threadlock.acquire()
						ProxyList.remove(ProxyList[rdint])
						threadlock.release()
						continue
					elif str(traceback.format_exc()).find('ProxyError')>0:
						threadlock.acquire()
						ProxyList.remove(ProxyList[rdint])
						threadlock.release()
						continue					
					else:
						continue

				try:
					if str(r.text).find('emind')>0:
						image_OCR.image_ocr('',spider_num)
						OcrFlag=False
						if Index!=1:
							Index-= 1
				#利用json库读取所需内容
					if OcrFlag:
						response=str(r.text).replace('\\','')
						count_pattern='"Count":"(\d+)"'
						court_pattern='"法院名称":"(.*?)"'
						DocID_pattern='"文书ID":"(.*?)"'
						CountResult=re.findall(count_pattern, response)
						CourtResult=re.findall(court_pattern, response)
						DocIDResult=re.findall(DocID_pattern, response)
						#判断是否有增量数据
						try:
							if TotalCount<int(CountResult[0]):
								OnlineCount=int(CountResult[0])
							else:
								print(LocalTime()+'yf爬虫'+str(spider_num)+':该法院未查到增量数据，跳入爬取下一个法院')
								break
						except:
							continue
						#获取文书ID
						for k in range(len(DocIDResult)):
							if DocIDResult[k] in CourtName_DocID :
								flag=True
							else:
								flag=False
								DocID.append(DocIDResult[k])
								IsPull.append(0)
								CreateTime.append(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
							if flag:
								pass
							else:
								if x!=CourtResult[k]:
									IsUpdateCourt=CourtResult[k]
								CourtName.append(CourtResult[k])								
							
						print (LocalTime()+'yf爬虫'+str(spider_num)+':正在获取'+x+':第'+str(Index)+'页的内容...')
						#SpiderLog.writeIndfoLog('yf爬虫'+str(spider_num)+':正在获取'+x+':第'+str(Index)+'页的内容...')
						#如果发现法院名称与数据库不一致的，以网站的为准更新数据库数据
						
						if IsUpdateCourt!='':
							threadlock.acquire()
							SqlHelper.UpdateCourt(x,IsUpdateCourt)
							threadlock.release()
							# print('更新法院成功')
						
						if OnlineCount-TotalCount==CounrtNum:
							threadlock.acquire()
							SqlHelper.UdateTotalCount(x, TotalCount)
							threadlock.release()
							break
						#当DcoID总量大于100时将DocID写入到数据库
						if len(DocID)>0:
							CounrtNum+=1
							df=pd.DataFrame({'CourtName':CourtName,'DocID':DocID,'IsPull':IsPull,'CreateTime':CreateTime})
							threadlock.acquire()
							SqlHelper.InputUrl(df=df)
							threadlock.release()				
							DocID=[]
							CourtName=[]
							IsPull=[]
							CreateTime=[]										
						#这一行是让程序休眠，避免产生验证码验证
						time.sleep(SleepNum)
					Index+=1
				except Exception as e:
					print(LocalTime()+'yf爬虫'+str(spider_num)+traceback.format_exc())
					#SpiderLog.writeIndfoLog('yf爬虫'+str(spider_num)+traceback.format_exc())
					#发生未知错误时，休眠1分钟后再尝试
					time.sleep(60)