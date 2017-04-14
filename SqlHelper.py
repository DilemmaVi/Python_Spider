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
	sql1='SELECT Court FROM [SpiderData].[dbo].CourtList where Court not in (select distinct courtname from SpiderUrl)'
	data=pd.read_sql(sql1, con)
	df=pd.DataFrame(data)
	return df

#将爬取到的案件链接写入到数据库中
def InputUrl(df=pd.DataFrame()):
	try:
		df.to_sql("SpiderUrl", scon,if_exists='append',index=False)
		return '导入数据成功！'
	except Exception as e:
		return '程序发生异常'
	

def CourtName_DocID(CourtName):
	term=str(CourtName)
	sql='select DocID from SpiderUrl where CourtName='+"'"+term+"'"
	data=pd.read_sql(sql, con)['DocID']
	df=set(data)
	return df

def GetUrlList():
	sql='select DocID from SpiderUrl where IsPull=0 order by createTime desc'
	data=pd.read_sql(sql, con)
	df=pd.DataFrame(data)['DocID']
	return df

def InsertContent(df=pd.DataFrame()):
	try:
		df.to_sql("LegalData", scon,if_exists='append',index=False)
		return 'Success'
	except Exception as e:
		return 'Error'

def UpdateUrl(url):
	sql='update SpiderUrl set IsPull=1 where DocID='+"'"+url+"'"
	cursor=con.cursor()
	cursor.execute(sql)
	con.commit()
	if cursor.rowcount==1:
		print('URL数据更新成功')

