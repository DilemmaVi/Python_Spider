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
import socket

def LocalTime():
	return time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))

def SendMessage(message):
	port=8081
	host='192.168.4.191'
	s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
	s.sendto(message.encode(encoding='utf-8'),(host,port))


# print (LocalTime()+':爬虫正在启动...')
SpiderLog.writeIndfoLog('爬虫正在启动...')
SendMessage(LocalTime()+':爬虫正在启动...')

while True:
	CourtData=SqlHelper.GetCourtList()['Court']
	# print(LocalTime()+':本次总共需要爬取'+str(len(CourtData))+'个法院的案件链接')
	SpiderLog.writeIndfoLog('本次总共需要爬取'+str(len(CourtData))+'个法院的案件链接')
	SendMessage(LocalTime()+':本次总共需要爬取'+str(len(CourtData))+'个法院的案件链接')
	# NOdata=[]
	DocID=[]
	CourtName=[]
	IsPull=[]
	CreateTime=[]
	url='http://wenshu.court.gov.cn/List/ListContent'
	try:
		for x in CourtData: 
			CourtName_DocID=SqlHelper.CourtName_DocID(x)
			# print (LocalTime()+':正在获取'+x+'的内容')
			SpiderLog.writeIndfoLog('正在获取'+x+'的内容')
			SendMessage(LocalTime()+':正在获取'+x+'的内容')	
			#这是页数、程序休息时间的定义和三个空的列表用来装筛选后的数据。
			Index=1
			SleepNum= 3
			count=100
			flag=False
			CountData=False
			IsUpdateCourt=''
			TotalCount='0'
			
			while Index <=count:
				OcrFlag=True
				my_headers={'User-Agent':'User-Agent:Mozilla/5.0(Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.95Safari/537.36 Core/1.50.1280.400',}

				#这一行是搜索条件，根据浏览器post内容得到，通过法院名称和页码来爬取所需链接
				data={'Param':'法院名称:' +x, 'Index': Index,'Page':'20','Order':'裁判日期','Direction':'desc'}
				
				try:
					#将网址、请求头、搜索条件等数据上传并取得内容
					r=req.post(url,headers=my_headers, data = data)
					#用 json解码取得的网页内容
					raw=r.json()
				except Exception as e:
					SendMessage(traceback.format_exc())
					SpiderLog.writeErrorLog(traceback.format_exc())
					if str(traceback.format_exc()).find('JSONDecodeError')>0:
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
									TotalCount=v
									count=math.ceil(int(v)/20) if math.ceil(int(v)/20)<=100 else 100

				# print (LocalTime()+':正在获取'+x+':第'+str(Index)+'页的内容...')
				SpiderLog.writeIndfoLog('正在获取'+x+':第'+str(Index)+'页的内容...')
				SendMessage(LocalTime()+':正在获取'+x+':第'+str(Index)+'页的内容...')	
				#如果发现法院名称与数据库不一致的，以网站的为准更新数据库数据
				if IsUpdateCourt!='':
					SqlHelper.UpdateCourt(x,IsUpdateCourt)
					# print('更新法院成功')
				SqlHelper.UdateTotalCount(x, TotalCount)				
				#当DcoID总量大于100时将DocID写入到数据库
				if len(DocID)>1:

					df=pd.DataFrame({'CourtName':CourtName,'DocID':DocID,'IsPull':IsPull,'CreateTime':CreateTime})
					SqlHelper.InputUrl(df=df)
					# print('更新数据成功')					
					DocID=[]
					CourtName=[]
					IsPull=[]
					CreateTime=[]										
				#这一行是让程序休眠，避免产生验证码验证
				time.sleep(SleepNum)
				if CountData:
					# print(LocalTime()+':该法院未查到数据，跳入爬取下一个法院')
					SendMessage(LocalTime()+':该法院未查到数据，跳入爬取下一个法院')
					# NOdata.append(x)
					Index+=101
				if flag:
					# print(LocalTime()+':发现重复内容，跳入爬取下一个法院')
					SpiderLog.writeIndfoLog('发现重复内容，跳入爬取下一个法院')
					SendMessage(LocalTime()+':发现重复内容，跳入爬取下一个法院')
					Index+=101
				else:
					Index+= 1
	except Exception as e:
		print(LocalTime()+traceback.format_exc())
		SpiderLog.writeErrorLog(traceback.format_exc())
		SendMessage(traceback.format_exc())
		# print(LocalTime()+'+遇到错误，休眠10分钟后重试')
		SendMessage(LocalTime()+':遇到错误，休眠10分钟后重试')
		#发生未知错误时，休眠10分钟后再尝试
		time.sleep(600)
	#对没有数据的法院进行记录
	# NOdf=pd.DataFrame({'Court':NOdata})
	# NOdf.to_excel(r'G:\1.xlsx',sheet_name='Sheet1')







