# coding=utf-8
__author__ = 'syq'

#https://github.com/tesseract-ocr
import sys
import time
import os
os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'
from pyocr import pyocr
from PIL import Image
import urllib.request
import requests as req
import SpiderLog


def image_ocr(proxies='',num=1):
	try:
		print('启动验证码识别程序...')
		SpiderLog.writeIndfoLog('启动验证码识别程序...')
		Index=1
		while Index<100:
			# my_headers={'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0',}
			if proxies=='':
				response=req.get('http://wenshu.court.gov.cn/User/ValidateCode')
			else:
				response=req.get('http://wenshu.court.gov.cn/User/ValidateCode',proxies=proxies)  
			html=response.content
		    #读取信息流，写图片
			with open('../image/'+str(num)+'.jpg', 'wb')as fp:
				fp.write(html)	
			time.sleep(2)
			#初始化验证码识别工具
			tools = pyocr.get_available_tools()[:]
			if len(tools) == 0:
				print("No OCR tool found")
				sys.exit(1)

			url='http://wenshu.court.gov.cn/Content/CheckVisitCode'

			#这一行是post的内容，即验证码
			try:
				data={'ValidateCode':tools[0].image_to_string(Image.open('../image/'+str(num)+'.jpg'),lang='eng')}
			except Exception as e:
				data={'ValidateCode':'0000'}
			 
			#验证码post
			if proxies=='':
				r=req.post(url, data = data)
			else:
				r=req.post(url,data = data,proxies=proxies)
			if r.text=='1':
				print ('识别成功！！！')
				SpiderLog.writeIndfoLog('识别成功！！！')
				Index+=100
			else:
				print ('第'+str(Index)+'次识别失败，正在重试...')
				SpiderLog.writeIndfoLog('第'+str(Index)+'次识别失败，正在重试...')
				Index+=1
		print ('重新启动爬虫程序...')
		SpiderLog.writeIndfoLog('重新启动爬虫程序...')	
	except Exception as e:
		print(e)
