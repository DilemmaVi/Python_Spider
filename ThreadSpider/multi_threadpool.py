# -*- coding: utf-8 -*-
import time
import threading
from time import ctime,sleep
import traceback
import SqlHelper
import math
import content_finall
import url_finall

#根据分组数获得法院分组list
def group_court(num):
	CourtList=SqlHelper.GetCourtList()
	group_courtlist=[]
	step=math.ceil(len(CourtList)/num)
	for i in range(0,len(CourtList),step):
		group_courtlist.append(CourtList[i:i+step])
	return group_courtlist

def url_threading(num):
	try:
		CourtList=SqlHelper.GetCourtList()
		group_courtlist=[]
		step=math.ceil(len(CourtList)/num)
		for i in range(0,len(CourtList),step):
			group_courtlist.append(CourtList[i:i+step])
		threadLock = threading.Lock()
		spider_num=[x+1 for x in range(num)] 
		thread_lkist=[]
		for  i in range(num):
			sthread=threading.Thread(target=url_finall.url_get,args=(int(spider_num[i]),threadLock,group_courtlist[i]))
			thread_lkist.append(sthread)
		for  i in range(num):
			thread_lkist[i].start()
	except Exception as e:
		print(traceback.format_exc())

def content_threading(num):
	try:

		threadLock = threading.Lock()
		spider_num=[x+1 for x in range(num)] 
		thread_lkist=[]
		for  i in range(num):
			sthread=threading.Thread(target=content_finall.content_get,args=(int(spider_num[i]),threadLock))
			thread_lkist.append(sthread)
		for  i in range(num):
			thread_lkist[i].start()
	except Exception as e:
		print(traceback.format_exc())

if __name__ == '__main__':
	# url_threading(3)
	content_threading(7)

