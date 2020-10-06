import socket
import ssl
import sys
from time import sleep
from sys import getsizeof
import math
import os

class Client():
    def __init__(self):
        #Config area
        self.ip = "mm.fritz.box"
        self.port = 499
        self.user = "admin"
        self.password = "Test123"
        self.sock = None
        self.BUFFER_SIZE = 4096
        #end of the conifg area

        self.online = True
        self.dic_s = {}
        self.dic = {}
        self.use_dic = {}
        self.use_dic.update({key: False} for key,  in list(self.dic_s.items()))
        self.context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        self.context.load_verify_locations('./.cert/example.crt')
        sock = socket.create_connection((self.ip, self.port))
        self.sock = self.context.wrap_socket(sock, server_hostname=self.ip)
        self.algo()
        self.stop()
        
    def algo(self):
        while self.online:
            self.recive("./log.lst")
            self.dic_s = {}
            f = open("./log.lst", "r")
            for line in f:
                try:
                    file,date = line.split(";")
                    self.dic_s.update({file: date})
                except:
                    pass
            for path, subdirs, files in os.walk("./storage/"):
                for name in files:
                    file = os.path.join(path, name)
                    date = str(os.path.getmtime(file))
                    self.dic.update({file: date})
            for key_s, values_s in list(self.dic_s.items()):
                for key, values in list(self.dic.items()):
                    if key == key_s:
                        self.use_dic.update({key: True})
                        if float(self.dic[key]) > float(self.dic_s[key_s]):
                            self.send(str(key))
                        elif float(self.dic[key]) < float(self.dic_s[key_s]):
                            self.recive(str(key))
                        else:
                            pass
            for key, value in list(self.use_dic.items()):
                if value != True:
                    self.recive(str(key))
                self.use_dic.update({key: False})

    def send(self,file):
        text = None
        f = open(file, "rb")#,encoding='ascii')
        text = f.read()
        #text = text.replace(" ","|-|")
        leng = getsizeof(text)

        leng = math.floor(getsizeof(text) / self.BUFFER_SIZE)
        rest = getsizeof(text) % self.BUFFER_SIZE

        self.sock.send(bytes("Header{send:"+str(leng)+":"+str(rest)+":"+file+"}","utf-8"))
        sleep(1)
        #for l in text:
        self.sock.send(text)
        print("Send file:",file)
        recv = str(self.sock.recv(2))[-2:-1]
        if recv == "OK":
            print("Everything was recived correctly")


    def recive(self,file):
        self.sock.send(bytes("Header{recive:"+file+"}", "utf-8"))
        msg = ""
        while "}" not in msg:
            msg = msg + str(self.sock.recv(1))[-2:-1] # msg = "Header{send:size:file}"or"Header{recive:file}"
        print("Incoming Header: ",msg)
        msg = msg.replace("Header{", "")
        msg = msg.replace("}", "")
        try:
            typ,size,rest,file =msg.split(":")
        except:
            typ,file =msg.split(":")
        if typ == "send":
            print("Reciver Mode")
            if int(size) > 0:

                l = self.sock.recv(self.BUFFER_SIZE)
            #for r in range(int(size)):
            if int(size) > 0:
                for r in range(int(size)-1):
                    l = l + self.sock.recv(self.BUFFER_SIZE)#[-2:-1]
                    #print(str(r), " of", size)
                #l = l.replace("|-|", " ")
                l = l + self.sock.recv(int(rest))
            elif int(size) == 0:
                l = self.sock.recv(int(rest))
            print("Recived erverything")
            self.sock.send(b"OK")
            #l = l.replace(" ","|-|")
            try:
               os.system("rm "+file)
            except:
                pass
            f = open(file,"wb")#,encoding='ascii')
            f.write(l)
            #f.write(t)
            f.close()
    def stop(self):
        self.config = False
        self.sock.close()
c = Client()
c.stop()