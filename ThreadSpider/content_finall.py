# -*- coding: utf-8 -*-  
import requests as req
import demjson
import pandas as pd
import SqlHelper
import json
import image_OCR
import urllib
import time
import re
import traceback
import SpiderLog
import random



def LocalTime():
	return time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))

def content_get(spider_name,thread_lock):
	time.sleep(int(spider_name/5))
	print('英华爬虫'+str(spider_name)+'----------start----------')

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
	print(LocalTime()+':正在获取待爬URL...')
	SpiderLog.writeContentIFLog('正在获取待爬URL...')
	'''
	案件相关信息
	'''
	Title=[]          #案件标题
	IssuedNumber=[]   #发文字号
	Court=[]          #法院名称
	TrialDate=[]      #裁判日期
	CaseType=[]       #案件类型
	TrialRound=[]     #审理程序
	content=[]        #正文
	Appellor=[]       #当事人，如无则为空
	LegalBase=[]      #相关法规
	CreateTime=[]     #创建时间，默认为当前系统时间
	AllData=[]        #爬取到的正文原始数据
	DocId_list=[]
	IsPull_list=[]
	try:
		#初始化待爬取链接
		global url_list
		thread_lock.acquire()
		url_list= list(SqlHelper.GetUrlList())
		thread_lock.release()
	except:
		print(traceback.format_exc())

	while True:	
		try:
			thread_lock.acquire()
			crawl_url=url_list[random.randint(0,len(url_list))]
			url_list.remove(crawl_url)
			if len(crawl_url)<1:
				crawl_url.extend(list(SqlHelper.GetUrlList()))
			if len(crawl_url)<10:
				time.sleep(600)	
				thread_lock.release()
				continue
			thread_lock.release()
			ls={'docId':crawl_url}
			index=0
		except:
			print(traceback.format_exc())
			continue
			#遍历URL进行信息爬取
		
		while True:
			try:
				index+=1
				print(LocalTime()+':正在获取'+ls['docId']+'的内容;\n本次为英华爬虫'+str(spider_name)+'第'+str(index)+'次爬取内容')
				SpiderLog.writeContentIFLog('正在获取'+ls['docId']+'的内容;\n本次为英华爬虫'+str(spider_name)+'第'+str(index)+'次爬取内容')
				LegalData=''
				LegalContentData=''
				AppellorData=''
				trialRoundData=''
				CaseTypeData=''
				TrialDateData=''
				CourtData=''
			
				LegalSummary=req.post('http://wenshu.court.gov.cn/Content/GetSummary',proxies=proxies,data=ls)
				LegalContent=req.get('http://wenshu.court.gov.cn/CreateContentJS/CreateContentJS.aspx?DocID='+ls['docId'],proxies=proxies)
				#判断获取内容是否正确，不正确可能是内部服务器问题，休眠5分钟再尝试爬取
				#判断是否需要验证码验证，如是启动验证码识别程序		
				if LegalContent.text.find('emind')>0:
					time.sleep(3)
					LegalSummary=req.post('http://wenshu.court.gov.cn/Content/GetSummary',data=ls,proxies=proxies)
					LegalContent=req.get('http://wenshu.court.gov.cn/CreateContentJS/CreateContentJS.aspx?DocID='+ls['docId'],proxies=proxies)
				if LegalContent.content.decode('utf-8').find('请开启JavaScript并刷新该页')>0:
					print('英华爬虫'+str(spider_name)+'请开启javascript')
					time.sleep(30)
					SpiderLog.writeContentIFLog('英华爬虫'+str(spider_name)+'请开启javascript')
					continue

				#获取概要信息
				try:
					result=demjson.decode(LegalSummary.json())
					files=str(LegalContent.content.decode('utf-8')).replace('\\','')
					#判断是否网站错误提供数据
					if dict(result)['RelateInfo']==[]:
						print('英华爬虫'+str(spider_name)+'网站提供的summary数据为空')
						SpiderLog.writeContentIFLog('英华爬虫'+str(spider_name)+'网站提供的summary数据为空')
						continue
					elif str(files).find('网站当前访问量较大')>0:
						print('英华爬虫'+str(spider_name)+'发现需要输入验证码')
						SpiderLog.writeContentIFLog('英华爬虫'+str(spider_name)+'发现需要输入验证码')
						continue
				except:
					print('英华爬虫'+str(spider_name)+'读取Summary异常')
					continue
				for x in result.get('RelateInfo'):
					if x.get('key')=='court':
						CourtData=x.get('value')	
					elif x.get('key')=='caseType':
						CaseTypeData=x.get('value')
					elif x.get('key')=='trialRound':
						trialRoundData=x.get('value')
					elif x.get('key')=='trialDate':
						TrialDateData=x.get('value')
					elif x.get('key')=='appellor':
						AppellorData=x.get('value')
				for x in result.get('LegalBase'):
					try:
						LegalData+=x.get('法规名称')+'\n'
					except Exception as e:
						pass
				for x in result.get('LegalBase'):
					for i in x.get('Items'):
						try:
							LegalData+=x.get('法条名称')+'\n'
							LegalData+=x.get('法条内容')
						except Exception as e:
							pass
				Court.append(CourtData)
				TrialRound.append(trialRoundData)
				CaseType.append(CaseTypeData)
				TrialDate.append(TrialDateData)
				if LegalData=='':
					LegalBase.append('无')
				else:
					LegalBase.append(LegalData)
				if AppellorData=='':
					Appellor.append('无')
				else:
					Appellor.append(AppellorData.replace('&times;','X'))



				#正则匹配获取正文内容
				pattern_Title=r'"Title":"(.*?)"'
				pattern_IssuedNumber=r"right;.*?>(.*?)</div>"
				pattern_Conten=r'>(.*?)<'

				AllData.append(files)
				
				try:
					Title.append(re.findall(pattern_Title, files)[0])
				except Exception as e:
					Title.append('')			
				try:
					IssuedNumber.append(re.findall(pattern_IssuedNumber, files)[0])
				except Exception as e:
					IssuedNumber.append('')
				
				Text=re.findall(pattern_Conten, files)
				for i in Text:
					try:
						LegalContentData+=i+'\n'
					except Exception as e:
						pass
				content.append(LegalContentData.replace('&times;','X').replace(r'\u3000',''))
				DocId_list.append(ls['docId'])
				IsPull_list.append('1')
				CreateTime.append(LocalTime())
				print('英华爬虫'+str(spider_name)+'目前有：'+str(len(DocId_list)))
				SpiderLog.writeContentIFLog('英华爬虫'+str(spider_name)+'目前有：'+str(len(DocId_list)))
				df=pd.DataFrame({'DocID':DocId_list,'Title':Title,'IssuedNumber':IssuedNumber,'Court':Court,'TrialDate':TrialDate,'CaseType':CaseType,
					'TrialRound':TrialRound,'Doc':content,'appellor':Appellor,'LegalBase':LegalBase,'CreateTime':CreateTime,'AllData':AllData})
				dt=pd.DataFrame({'DocID':DocId_list,'IsPull':IsPull_list})
				if len(DocId_list)>50:
					thread_lock.acquire()
					DataInsert=SqlHelper.InsertContent(df)
					if DataInsert=='Success':
						SqlHelper.UpdateUrl(dt)
					thread_lock.release()
					#清空list
					DocId_list=[]
					IsPull_list=[]
					Title=[]          
					IssuedNumber=[]   
					Court=[]         
					TrialDate=[]     
					CaseType=[]       
					TrialRound=[]     
					content=[]        
					Appellor=[]       
					LegalBase=[]     
					CreateTime=[]     
					AllData=[]        
				break
			except Exception as e:
				print(len(DocId_list))
				print(len(Title))
				print(len(IssuedNumber))
				print(len(Court))
				print(len(TrialDate))
				print(len(TrialRound))
				print(len(content))
				print(len(Appellor))
				print(len(LegalBase))
				print(len(CreateTime))
				print(len(AllData))
				print(len(CaseType))
				print(traceback.format_exc())
				if str(traceback.format_exc()).find('aborted')>0:
					time.sleep(300)
				if index>5:
					break
				else:
					continue

