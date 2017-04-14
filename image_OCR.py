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

def image_ocr():
	print('启动验证码识别程序...')
	SpiderLog.writeIndfoLog('启动验证码识别程序...')
	Index=1
	while Index<100:
		response=urllib.request.urlopen('http://wenshu.court.gov.cn/User/ValidateCode')  
		html=response.read()
	    #读取信息流，写图片
		with open('1.jpg', 'wb')as fp:
			fp.write(html)	
		time.sleep(2)
		#初始化验证码识别工具
		tools = pyocr.get_available_tools()[:]
		if len(tools) == 0:
			print("No OCR tool found")
			sys.exit(1)

		url='http://wenshu.court.gov.cn/Content/CheckVisitCode'
		my_headers={'User-Agent':'User-Agent:Mozilla/5.0(Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.95Safari/537.36 Core/1.50.1280.400',}

		#这一行是post的内容，即验证码
		data={'ValidateCode':tools[0].image_to_string(Image.open('1.jpg'),lang='eng')}
		 
		#验证码post
		r=req.post(url,headers=my_headers, data = data)
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

if __name__ == '__main__':
	image_ocr()