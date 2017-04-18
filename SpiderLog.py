# encoding:utf-8
import sys
import logging
import time
from logging.handlers import TimedRotatingFileHandler
from logging.handlers import RotatingFileHandler
import re
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
#写url运行日志
def writeIndfoLog(message):
	log_fmt = '%(asctime)s\t%(levelname)s: %(message)s'
	formatter = logging.Formatter(log_fmt)
	log_file_handler = TimedRotatingFileHandler(filename='./Log/UrlInfoLog/'+"UrlInfoLog", when="D", interval=1, backupCount=90)
	log_file_handler.suffix = "%Y-%m-%d_%H-%M.log"
	log_file_handler.extMatch = re.compile(r"^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}.log$")
	log_file_handler.setFormatter(formatter)
	log_file_handler.setLevel(logging.INFO)
	log = logging.getLogger()
	log.setLevel(logging.NOTSET)
	log.addHandler(log_file_handler)
	log.info(message)
	log.removeHandler(log_file_handler)

#写url错误日志
def writeErrorLog(message):
	log_fmt = '%(asctime)s\t%(levelname)s: %(message)s'
	formatter = logging.Formatter(log_fmt)
	log_file_handler = TimedRotatingFileHandler(filename='./Log/UrlErrorLog/'+"UrlErrorLog", when="D", interval=1, backupCount=90)
	log_file_handler.suffix = "%Y-%m-%d_%H-%M.log"
	log_file_handler.extMatch = re.compile(r"^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}.log$")
	log_file_handler.setFormatter(formatter)
	log_file_handler.setLevel(logging.INFO)
	log = logging.getLogger()
	log.setLevel(logging.NOTSET)
	log.addHandler(log_file_handler)
	log.error(message)
	log.removeHandler(log_file_handler)

#写正文爬虫运行日志
def writeContentIFLog(message):
	log_fmt = '%(asctime)s\t%(levelname)s: %(message)s'
	formatter = logging.Formatter(log_fmt)
	log_file_handler = TimedRotatingFileHandler(filename='./Log/ContentInfoLog/'+"ContentInfoLog", when="D", interval=1, backupCount=90)
	log_file_handler.suffix = "%Y-%m-%d_%H-%M.log"
	log_file_handler.extMatch = re.compile(r"^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}.log$")
	log_file_handler.setFormatter(formatter)
	log_file_handler.setLevel(logging.INFO)
	log = logging.getLogger()
	log.setLevel(logging.NOTSET)
	log.addHandler(log_file_handler)
	log.info(message)
	log.removeHandler(log_file_handler)

def writeContentERLog(message):
	log_fmt = '%(asctime)s\t%(levelname)s: %(message)s'
	formatter = logging.Formatter(log_fmt)
	log_file_handler = TimedRotatingFileHandler(filename='./Log/ContentErrorLog/'+"ContentErrorLog", when="D", interval=1, backupCount=90)
	log_file_handler.suffix = "%Y-%m-%d_%H-%M.log"
	log_file_handler.extMatch = re.compile(r"^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}.log$")
	log_file_handler.setFormatter(formatter)
	log_file_handler.setLevel(logging.INFO)
	log = logging.getLogger()
	log.setLevel(logging.NOTSET)
	log.addHandler(log_file_handler)
	log.error(message)
	log.removeHandler(log_file_handler)