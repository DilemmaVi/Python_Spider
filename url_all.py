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


def LocalTime():
	return time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))

print (LocalTime()+':yf爬虫正在启动...')
SpiderLog.writeIndfoLog('yf爬虫正在启动...')

while True:
	try:
		DataCount=SqlHelper.GetCourtList()['Court']
		print(LocalTime()+'yf爬虫:本次总共需要爬取'+str(len(DataCount))+'个法院的案件链接')
		SpiderLog.writeIndfoLog('yf爬虫:本次总共需要爬取'+str(len(DataCount))+'个法院的案件链接')
		# NOdata=[]
		DocID=[]
		CourtName=[]
		IsPull=[]
		CreateTime=[]
		url='http://wenshu.court.gov.cn/List/ListContent'
	except Exception as e:
		pass
	for x in DataCount: 
		CourtName_DocID=SqlHelper.CourtName_DocID(x)
		print (LocalTime()+'yf爬虫:正在获取'+x+'的内容')
		SpiderLog.writeIndfoLog('yf爬虫:正在获取'+x+'的内容')
		#这是页数、程序休息时间的定义和三个空的列表用来装筛选后的数据。
		Index=1
		CounrtNum=0#判断是否已经更新完了当前法院的全部数据
		SleepNum= 3
		count=100
		flag=False
		CountData=False
		IsUpdateCourt=''
		TotalCount=int(SqlHelper.CourtName_TotalCount(x))
		while Index <=count:
			OcrFlag=True
			my_headers={'User-Agent':'Mozilla/5.0(Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.95Safari/537.36 Core/1.50.1280.400'}

			#这一行是搜索条件，根据浏览器post内容得到，通过法院名称和页码来爬取所需链接
			data={'Param':'法院名称:' +x, 'Index': Index,'Page':'20','Order':'裁判日期','Direction':'desc'}
			
			try:
				#将网址、请求头、搜索条件等数据上传并取得内容
				r=req.post(url,headers=my_headers, data = data)
				#用 json解码取得的网页内容
				raw=r.json()
			except Exception as e:
				SpiderLog.writeErrorLog(str(data)+traceback.format_exc())
				if str('yf爬虫:'+traceback.format_exc()).find('JSONDecodeError')>0:
					continue
				else:
					print('网站封闭IP，休眠十分钟后重试！！！')					
					time.sleep(600)


			try:
			#利用json库读取所需内容
				jsondata = json.loads(raw)
			#产生异常时尝试自动识别验证码
			except:
				image_OCR.image_ocr()
				OcrFlag=False
				if Index!=1:
					Index-= 1
			try:
				if OcrFlag:
					for ls in jsondata:
						if flag:
							break
						else:
							for (k,v) in ls.items():
								if k=='文书ID':
									if v in CourtName_DocID :
										flag=True
									else:
										flag=False
										DocID.append(v)
										IsPull.append(0)
										CreateTime.append(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
								if k=='法院名称':
									if flag:
										pass
									else:
										if x!=v:
											IsUpdateCourt=v
										CourtName.append(v)	
								if k=='Count' and int(v)==0:
									CountData=True
								if count==100 and k=='Count':
									if TotalCount<int(v):
										TotalCount=int(v)
									else:
										CountData=True
									count=math.ceil(int(v)/20) if math.ceil(int(v)/20)<=100 else 100

				print (LocalTime()+'yf爬虫:正在获取'+x+':第'+str(Index)+'页的内容...')
				SpiderLog.writeIndfoLog('yf爬虫:正在获取'+x+':第'+str(Index)+'页的内容...')
				#如果发现法院名称与数据库不一致的，以网站的为准更新数据库数据
				if IsUpdateCourt!='':
					SqlHelper.UpdateCourt(x,IsUpdateCourt)
					# print('更新法院成功')
				if TotalCount-int(SqlHelper.CourtName_TotalCount(x))==CounrtNum:
					CountData=True
					SqlHelper.UdateTotalCount(x, TotalCount)				
				#当DcoID总量大于100时将DocID写入到数据库
				if len(DocID)>0:
					CounrtNum+=1
					df=pd.DataFrame({'CourtName':CourtName,'DocID':DocID,'IsPull':IsPull,'CreateTime':CreateTime})
					SqlHelper.InputUrl(df=df)				
					DocID=[]
					CourtName=[]
					IsPull=[]
					CreateTime=[]										
				#这一行是让程序休眠，避免产生验证码验证
				time.sleep(SleepNum)
				if CountData:
					print(LocalTime()+'yf爬虫:该法院未查到增量数据，跳入爬取下一个法院')
					SpiderLog.writeIndfoLog('yf爬虫:该法院未查到增量数据，跳入爬取下一个法院')
					# NOdata.append(x)
					break
				else:
					Index+=1
			except Exception as e:
				print(traceback.format_exc())
				SpiderLog.writeIndfoLog('yf爬虫:'+traceback.format_exc())
				#发生未知错误时，休眠1分钟后再尝试
				time.sleep(60)







