# -*- coding: utf-8 -*-  
import pymssql
import pandas as pd
from sqlalchemy import create_engine
import SpiderLog

con = pymssql.connect(host='192.168.0.186', user='sa', password='bdyh@2016', database='SpiderData')
scon = create_engine('mssql+pymssql://sa:bdyh@2016@192.168.0.186/SpiderData')

#从数据库获取法院列表
def GetCourtList():
	sql='select Court from CourtList'
	#sql1='SELECT Court FROM [SpiderData].[dbo].CourtList where Court not in (select distinct courtname from SpiderUrl)'
	data=pd.read_sql(sql, con)
	df=pd.DataFrame(data)['Court']
	return df

#将爬取到的案件链接写入到数据库中
def InputUrl(df=pd.DataFrame()):
	try:
		df.to_sql("SpiderUrl", scon,if_exists='append',index=False)
		return '导入数据成功！'
	except Exception as e:
		return '程序发生异常'
	
#通过法院名称获取DocID，用于判断重复数据
def CourtName_DocID(CourtName):
	term=str(CourtName)
	sql='select DocID from SpiderUrl where CourtName='+"'"+term+"'"
	data=pd.read_sql(sql, con)['DocID']
	df=set(data)
	return df

#通过法院名称获取法院数据量，对比网站数据量判断是否需要爬取
def CourtName_TotalCount(CourtName):
	term=str(CourtName)
	sql='select TotalCount from CourtList where Court='+"'"+term+"'"
	data=pd.read_sql(sql, con)['TotalCount']
	return data

#获取待爬取的URL数据
def GetUrlList(num=0):
	sql='select distinct top(5000) DocID,CreateTime from SpiderUrl where IsPull=0 order by createTime desc'
	num1=num*1000+1
	num2=num*1000+1000
	sql1='select * from (select *,ROW_NUMBER() OVER (order by createtime desc) AS ROWNUM from SpiderUrl where IsPull=0) t where ROWNUM between '+str(num1) +' and '+ str(num2)
	data=pd.read_sql(sql1, con)
	df=pd.DataFrame(data)['DocID']
	return df

#将获取到的正文插入到数据库
def InsertContent(df=pd.DataFrame()):
	try:
		df.to_sql("LegalData", scon,if_exists='append',index=False)
		return 'Success'
	except Exception as e:
		return 'Error'

#将爬完的数据进行标识
def UpdateUrl(url):
	sql='update SpiderUrl set IsPull=1 where DocID='+"'"+url+"'"
	cursor=con.cursor()
	cursor.execute(sql)
	con.commit()
	if cursor.rowcount==1:
		print('URL数据更新成功')

#通过excel表导入法院名称数据到数据库
def  InsertCourtData():
	df=pd.read_excel(r'C:\Users\YF-INT6\Downloads\审理法院列表.xlsx')
	df.rename(columns={'审理法院列表':'Court'},inplace=True)
	print(df)
	df.to_sql("CourtList",scon,if_exists='append',index=False)

#发现与网站法院名称不一致时，更新最新数据到数据库
def UpdateCourt(OldCourtName,NewCourtName):
	term1=str(OldCourtName)
	term2=str(NewCourtName)
	sql='UPDATE [SpiderData].[dbo].[CourtList] SET [Court] = '+"'"+term2+"'" +'WHERE Court='+"'"+term1+"'"
	cursor=con.cursor()
	cursor.execute(sql)
	con.commit()

def UdateTotalCount(CourtName,TotalCount):
	sql='UPDATE [SpiderData].[dbo].[CourtList] SET TotalCount = '+str(TotalCount)+'WHERE Court='+"'"+CourtName+"'"
	cursor=con.cursor()
	cursor.execute(sql)
	con.commit()

#
def InsertProxy(df=pd.DataFrame()):
	try:
		df.to_sql('Proxy', scon,if_exists='append',index=False)
		return 'Success'
	except Exception as e:
		return e

#获取代理ip数据
def GetProxyList():
	sql='select * from Proxy'
	data=pd.read_sql(sql, con)
	df=pd.DataFrame(data)['Proxy']
	return list(df)

if __name__ == '__main__':
	print(list(GetCourtList()[0:3]))