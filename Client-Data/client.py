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
        self.BUFFER_SIZE = 2048


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
            l = self.sock.recv(self.BUFFER_SIZE)
            #for r in range(int(size)):
            for r in range(int(size)-1):
               l = l + self.sock.recv(self.BUFFER_SIZE)#[-2:-1]
                #print(str(r), " of", size)
            #l = l.replace("|-|", " ")
            l = l + self.sock.recv(int(rest))
            print("Recived erverything")
            self.sock.send(b"OK")
            #l = l.replace(" ","|-|")
            try:
               os.system("rm ./storage/"+file)
            except:
                pass
            f = open("./storage/"+file,"wb")#,encoding='ascii')
            f.write(l)
            #f.write(t)
            f.close()
    def stop(self):
        self.sock.close()
c = Client()
c.recive(sys.argv[1])
c.stop()