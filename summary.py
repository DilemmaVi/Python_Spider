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

def LocalTime():
	return time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))




data=[]           #URL列表
#浏览器头部信息
my_headers={'User-Agent':'User-Agent:Mozilla/5.0(Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.95Safari/537.36 Core/1.50.1280.400',}
print(LocalTime()+':正在启动爬虫程序....')
#获取需爬取信息的URL
while True:	
	for x in SqlHelper.GetUrlList():
		data.append({'docId':x})
	print(LocalTime()+':正在获取待爬URL...')
	print(LocalTime()+':本次需要爬取URL总数为：'+str(len(data)))
	if len(data)==0:
		time(600)
		continue
	index=0
	#遍历URL进行信息爬取
	for ls in data:
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
		index+=1
		print(LocalTime()+':正在获取'+ls['docId']+'的内容;\n本次为英华爬虫第'+str(index)+'次爬取内容')
		LegalData=''
		LegalContentData=''
		AppellorData=''
		trialRoundData=''
		CaseTypeData=''
		TrialDateData=''
		try:
			LegalSummary=req.post('http://wenshu.court.gov.cn/Content/GetSummary',headers=my_headers,data=ls)
			time.sleep(3)
			LegalContent=req.get('http://wenshu.court.gov.cn/CreateContentJS/CreateContentJS.aspx?DocID='+ls['docId'],
				headers=my_headers)
			#判断获取内容是否正确，不正确可能是内部服务器问题，休眠5分钟再尝试爬取
			if LegalContent.content.decode('utf-8').find('请开启JavaScript并刷新该页')>0:
				print(LocalTime()+':遇到错误，休眠5分钟后重试')
				time.sleep(300)
				continue
			#判断是否需要验证码验证，如是启动验证码识别程序		
			if LegalContent.text.find('VisitRemind')>0:
				image_OCR.image_ocr()
				LegalSummary=req.post('http://wenshu.court.gov.cn/Content/GetSummary',headers=my_headers,data=ls)
				time.sleep(5)
				LegalContent=req.get('http://wenshu.court.gov.cn/CreateContentJS/CreateContentJS.aspx?DocID='+ls,
					headers=my_headers)

			#获取概要信息
			result=demjson.decode(LegalSummary.json())
			for x in result.get('RelateInfo'):
				if x.get('key')=='court':
					Court.append(x.get('value'))
					CreateTime.append(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
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

			#获取正文信息,因json解析常出错，改为正则匹配
			# re_pattern=' = "(.*?)";'
			# JsonData=demjson.decode(str(re.findall(re_pattern,LegalContent.content.decode('utf-8'))).replace(r'\\',''))
			# pattern_IssuedNumber=r"right;.*?>(.*?)</div>"
			# pattern_Title=r'"Title":"(.*?)"'
			# pattern_Conten=r'>(.*?)<'
			# Title.append(re.findall(pattern_Title, str(JsonData))[0])
			# IssuedNumber.append(re.findall(pattern_IssuedNumber, str(JsonData))[0])
			# text=re.findall(pattern_Conten, str(JsonData))
			# for ts in text:
			# 	if ts=='':
			# 		text.remove(ts)
			# for i in text:
			# 	try:
			# 		LegalContentData+=i+'\n'
			# 	except Exception as e:
			# 		pass

			#正则匹配获取正文内容
			pattern_Title=r'"Title":"(.*?)"'
			pattern_IssuedNumber=r"right;.*?>(.*?)</div>"
			pattern_Conten=r'>(.*?)<'
			files=str(LegalContent.content.decode('utf-8')).replace('\\','')
			Title.append(re.findall(pattern_Title, files)[0])
			IssuedNumber.append(re.findall(pattern_IssuedNumber, files)[0])
			Text=re.findall(pattern_Conten, files)
			for i in Text:
				try:
					LegalContentData+=i+'\n'
				except Exception as e:
					pass
			#如果标题为空，则跳过	
			if Title[0]=='':
				pass
			else:
				content.append(LegalContentData.replace('&times;','X').replace(r'\u3000',''))

			# print('Title:'+str(len(Title))+'IssuedNumber:'+str(len(IssuedNumber))+'Title:'+str(len(Court))+'TrialDate:'+str(len(TrialDate))
			# 	+'CaseType:'+str(len(CaseType))+'TrialRound:'+str(len(TrialRound))+'content:'+str(len(content))+'Appellor:'+str(len(Appellor))
			# 	+'LegalBase:'+str(len(LegalBase))+'CreateTime:'+str(len(CreateTime)))
				df=pd.DataFrame({'DocID':ls['docId'],'Title':Title,'IssuedNumber':IssuedNumber,'Court':Court,'TrialDate':TrialDate,'CaseType':CaseType,
					'TrialRound':TrialRound,'Doc':content,'appellor':Appellor,'LegalBase':LegalBase,'CreateTime':CreateTime})
				DataInsert=SqlHelper.InsertContent(df)
				if DataInsert=='Success':
					SqlHelper.UpdateUrl(ls['docId'])
				time.sleep(5)
		except Exception as e:
			print(LocalTime()+traceback.format_exc())
			if str(traceback.format_exc()).find('Failed to establish a new connection')>0:
				time.sleep(60)
			elif str(traceback.format_exc()).find('JSONDecodeError')>0:
				time.sleep(10)
			elif str(traceback.format_exc()).find('JsonData')>0:
				time.sleep(10)	
			else:
				print(LocalTime()+':遇到错误，休眠10分钟后重试')
				#发生未知错误时，休眠10分钟后再尝试
				time.sleep(600)

   