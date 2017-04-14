import socket


def SendMessage(message):
	port=8081
	host='192.168.4.191'
	s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
	s.sendto(message.encode(encoding='utf-8'),(host,port))