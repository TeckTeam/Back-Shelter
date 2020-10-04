import socket
import ssl
import sys
from time import sleep
from sys import getsizeof
import math

class Client():
    def __init__(self):
        self.ip = "mm.fritz.box"
        self.port = 499
        self.user = "admin"
        self.password = "Test123"
        self.sock = None
        self.BUFFER_SIZE = 1024


        self.context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        self.context.load_verify_locations('./.cert/example.crt')
        sock = socket.create_connection((self.ip, self.port))
        self.sock = self.context.wrap_socket(sock, server_hostname=self.ip)
        



    def send(self,file):
        text = None
        f = open("./storage/"+file, "rb")#,encoding='ascii')
        text = f.read()
        #text = text.replace(" ","|-|")
        leng = getsizeof(text)

        leng = math.floor(getsizeof(text) / self.BUFFER_SIZE)
        rest = getsizeof(text) % self.BUFFER_SIZE

        self.sock.send(bytes("Header{send:"+str(leng)+":"+str(rest)+":"+file+"}","utf-8"))
        sleep(5)
        #for l in text:
        self.sock.send(text)
        print("Send file:",file)
        recv = str(self.sock.recv(2))[-2:-1]
        if recv == "OK":
            print("Everything was recived correctly")


    def recive(self,sock):
        passtext = text.replace(" ","|-|")
    def stop(self):
        self.sock.close()
c = Client()
c.send("test.jpg")
c.stop()