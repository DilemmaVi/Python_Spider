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

#获取法院TotalCount数据
def cc_data():
	sql='select * from CourtList'
	data=pd.read_sql(sql, con)
	df=pd.DataFrame(data)
	return df

#获取待爬取的URL数据
def GetUrlList():
	try:
		sql='select distinct DocID,CreateTime from SpiderUrl where IsPull=0 order by createTime desc'
		# num1=num*5000+1
		# num2=num*5000+5000
		# sql1='select * from (select *,ROW_NUMBER() OVER (order by createtime desc) AS ROWNUM from SpiderUrl where IsPull=0) t where ROWNUM between '+str(num1) +' and '+ str(num2)
		data=pd.read_sql(sql, con)
		df=pd.DataFrame(data)['DocID']
		return df
	except:
		return 'error'

#将获取到的正文插入到数据库
def InsertContent(df=pd.DataFrame()):
	try:
		df.to_sql("LegalData", scon,if_exists='append',index=False)
		return 'Success'
	except Exception as e:
		return 'Error'

#将爬完的数据进行标识
def UpdateUrl(df=pd.DataFrame()):
	try:
		#sql='update SpiderUrl set IsPull=1 where DocID='+"'"+url+"'"
		del_sql='delete from cursorTB where 1=1'
		upt_sql='update SpiderUrl set SpiderUrl.IsPull=cursorTB.IsPull  from SpiderUrl,cursorTB where SpiderUrl.DocID=cursorTB.DocID'
		cursor=con.cursor()
		cursor.execute(del_sql)
		con.commit()
		df.to_sql('cursorTB', scon,if_exists='append',index=False)
		cursor.execute(upt_sql)
		con.commit()
		if cursor.rowcount>1:
			print('URL数据更新成功')
	except:
		pass

#通过excel表导入法院名称数据到数据库
def  InsertCourtData():
	df=pd.read_excel(r'C:\Users\YF-INT6\Desktop\court.xlsx')
	df.rename(columns={'法院名称':'Court'},inplace=True)
	print(df)
	df.to_sql("CourtNew",scon,if_exists='append',index=False)

#发现与网站法院名称不一致时，更新最新数据到数据库
def UpdateCourt(OldCourtName,NewCourtName):
	term1=str(OldCourtName)
	term2=str(NewCourtName)
	sql='UPDATE [SpiderData].[dbo].[CourtList] SET [Court] = '+"'"+term2+"'" +'WHERE Court='+"'"+term1+"'"
	cursor=con.cursor()
	cursor.execute(sql)
	con.commit()

def UdateTotalCount(CourtName,TotalCount):
	try:
		sql='UPDATE [SpiderData].[dbo].[CourtList] SET TotalCount = '+str(TotalCount)+'WHERE Court='+"'"+CourtName+"'"
		cursor=con.cursor()
		cursor.execute(sql)
		con.commit()
	except:
		pass

#
def InsertProxy(df=pd.DataFrame()):
	try:
		df.to_sql('Proxy', scon,if_exists='append',index=False)
		return 'Success'
	except Exception as e:
		print(e)

#获取代理ip数据
def GetProxyList():
	sql='select * from Proxy'
	data=pd.read_sql(sql, con)
	df=pd.DataFrame(data)['Proxy']
	return list(df)

if __name__ == '__main__':
	DocID=['00001f22-9962-4c13-90cc-a75200f9800f','0000542e-e0ab-4782-918f-f2d13cea4100']
	IsPull=['1','1']
	df=pd.DataFrame({'DocID':DocID,'IsPull':IsPull})
	UpdateUrl(df)

