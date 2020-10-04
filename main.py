import socket
from _thread import start_new_thread as thread
import os
from time import sleep
import ssl
class Server():
    #Startup
    def __init__(self):
        #Settings
        self.ip = "0.0.0.0"
        self.data_port = 499
        self.controll_port = 466
        self.cache = "./cache/"
        self.storage = "./storage/"
        self.users = ["admin"]
        self.passwds = ["Test123"]
        self.BUFFER_SIZE = 2048
        self.mode = True
        self.context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        self.context.load_cert_chain('./.cert/example.crt', './.cert/private.key')

        #Clients
        self.data_client = []
        self.data_addr = []
        self.data_activ = []
        self.data_sock_d = None
        self.controll_client = []
        self.controll_addr = []
        self.controll_activ = []
        self.controll_sock_d = None

        #startup
        self.startup()
        
    def startup(self):
        try:
            self.start_data()
            self.start_controller()

            
        except:
            print("Service Stop")
            self.stop()
            exit()
        thread(self.data,(1,))
        thread(self.controll,(1,))
    def start_controller(self):
        self.controll_sock_d = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.controll_sock_d.bind((self.ip,self.controll_port))
        self.controll_sock_d.listen()
        self.controll_sock = self.context.wrap_socket(self.controll_sock_d, server_side=True)
        print("Controller-Port: open")
    def start_data(self):
        self.data_sock_d = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.data_sock_d.bind((self.ip,self.data_port))
        self.data_sock_d.listen()
        self.data_sock = self.context.wrap_socket(self.data_sock_d, server_side=True)
        print("Data-Port: open")
    def data(self,l):
        while True:
            conn, addr = self.data_sock.accept()
            print("Connected to", addr)
            if len(self.data_client) == len(self.data_addr):
                i = len(self.data_addr)
                self.data_client.append(conn)
                self.data_addr.append(addr)
                self.data_activ.append(True)
                thread(self.client,(i,"data"))
            else:
                print("Connection lost to", addr)
    def controll(self,l):
        while True:
            conn, addr = self.controll_sock.accept()
            print("Connected to", addr)
            if len(self.controll_client) == len(self.controll_addr):
                i = len(self.controll_addr)
                self.controll_client.append(conn)
                self.controll_addr.append(addr)
                self.controll_activ.append(True)
                thread(self.client,(i,"controll"))
            else:
                print("Connection lost to", addr)
    def shell(self, sock, usr):
        shell = True
        path = "./"
        while shell:
            sock.send(bytes("\n"+ usr +":"+path+ "# ", "utf-8"))
            command = ""
            while "!" not in command:
                command = command + str(sock.recv(1))[-2:-1]
            command = command.replace("!", "")
            #print(command)
            command = command[1:]
            print(command)
            if command == "help":
                sock.send(b"<--------------------------------------------->\n")
                sock.send(bytes(" Help for "+usr+"\n", "utf-8"))
                sock.send(b" help          -> shows this page\n") #
                sock.send(b" ls {dir}      -> shows the content of the dir\n") #
                sock.send(b" cd {dir}      -> move in the dir\n")#
                sock.send(b" dir           -> show the path where you are\n") #
                sock.send(b" mkdir {}      -> create new dir\n")#
                sock.send(b" touch {}      -> create new file\n")#
                sock.send(b" rm {file}     -> remove file\n")#
                sock.send(b" rm -r {dir}   -> remove dir\n")#
                sock.send(b" connections   -> show all connections\n")#
                sock.send(b" upload {}     -> upload file or dir\n")
                sock.send(b" download {}   -> download file or dir\n")
                sock.send(b" exit          -> exits this session\n") #
                sock.send(b" shutdown      -> shutdown the server\n") #
                sock.send(b" reboot        -> reboot the server\n") 
                sock.send(b"<--------------------------------------------->\n")
            elif command == "reboot":
                sock.send(b"The server reboots now.\n")
                self.stop()
                self.startup()
            elif command == "shutdown":
                sock.send(b"The server shutdowns now.\n")
                self.mode = False
            elif command == "exit":
                shell = False
                sock.close()
            elif command == "dir":
                sock.send(bytes(path+"\n","utf-8"))
            elif command == "ls":
                if path == "./":
                    t = os.popen("ls -d "+path+"*/").read()
                else:
                    t = os.popen("ls "+path).read()
                sock.send(bytes(t,"utf-8"))
            elif "cd " in command:
                command = command.replace("cd ", "")
                if ".." in command:
                    t = path.split("/")
                    path = ""
                    for i in range(len(t)-2):
                        path = path + t[i] + "/"
                elif os.path.isdir(path+command):
                    path = path + command
                else:
                    sock.send(bytes("\n Path not found: "+command, "utf-8"))
            elif "mkdir " in command:
                command = command.replace("mkdir ", "")
                try:
                    os.system("mkdir "+path+command)
                except:
                    sock.send(bytes("Can't create the dir "+command,"utf-8"))
            elif "touch " in command:
                command = command.replace("touch ", "")
                try:
                    os.system("touch "+path+command)
                except:
                    sock.send(bytes("can't create the file "+command,"utf-8"))
            elif "rm -r" in command:
                command = command.replace("rm -r ", "")
                os.system("rm -r "+path+command)
                sock.send(b"Dir was deleted")
            elif "rm " in command:
                command = command.replace("rm ", "")
                os.system("rm "+path+command)
                sock.send(b"File was deleted")
            elif "connections" == command:
                sock.send(b"<------------------Data---------------------->\n")
                for i in range(len(self.data_addr)):
                    addr, port = self.data_addr[i]
                    if self.data_activ[i] == True:
                        sock.send(bytes("  "+str(i+1)+".Client "+addr+"\n","utf-8"))
                sock.send(b"<----------------Controll-------------------->\n")
                for i in range(len(self.controll_addr)):
                    addr, port = self.controll_addr[i]
                    if self.controll_activ[i] ==  True:
                        sock.send(bytes("  "+str(i+1)+". Client "+addr+"\n","utf-8"))
            else:
                sock.send(b"Command can't found")
    def client(self, i, set):
        if set == "data": #Data Transfer
            while True:
                sock = self.data_client[i]
                msg = ""
                while "}" not in msg:
                    msg = msg + str(sock.recv(1))[-2:-1] # msg = "Header{send:size:file}"or"Header{recive:size:file}"
                print("Incoming Header: ",msg)
                msg = msg.replace("Header{", "")
                msg = msg.replace("}", "")
                typ,size,rest,file =msg.split(":")
                if typ == "send":
                    print("Reciver Mode")
                    l = sock.recv(self.BUFFER_SIZE)
                    #for r in range(int(size)):
                    for r in range(int(size)-1):
                        l = l + sock.recv(self.BUFFER_SIZE)#[-2:-1]
                        #print(str(r), " of", size)
                    #l = l.replace("|-|", " ")
                    l = l + sock.recv(int(rest))
                    print("Recived erverything")
                    sock.send(b"OK")
                    #l = l.replace(" ","|-|")
                    try:
                        os.system("rm ./cache/"+file)
                    except:
                        pass
                    f = open("./cache/"+file,"wb")#,encoding='ascii')
                    f.write(l)
                    #f.write(t)
                    f.close()
                    
                elif typ == "recive":
                    pass

        elif set == "controll":  #Admin Terminal
                sock = self.controll_client[i]
                sock.send(b" ____             _        ____  _          _ _            \n")
                sock.send(b"| __ )  __ _  ___| | __   / ___|| |__   ___| | |_ ___ _ __ \n")
                sock.send(b"|  _ \ / _` |/ __| |/ /___\___ \| '_ \ / _ \ | __/ _ \ '__|\n")
                sock.send(b"| |_) | (_| | (__|   <_____|__) | | | |  __/ | ||  __/ |   \n")
                sock.send(b"|____/ \__,_|\___|_|\_\   |____/|_| |_|\___|_|\__\___|_|   \n")
                sock.send(b"Login:")
                usr = ""
                while " " not in usr:
                    usr = usr + str(sock.recv(1))[-2:-1]
                usr = usr.replace(" ", "")
                for u in range(len(self.users)):
                    if usr == self.users[u]:
                        sock.send(b"Password:")
                        pd = ""
                        while " " not in pd:
                            pd = pd + str(sock.recv(1))[-2:-1]
                        pd = pd.replace(" ", "")
                        pd = pd.replace("\n", "")
                        print(pd)
                if usr == self.users[u] and pd == "n" + self.passwds[u]:
                    sleep(2)
                    sock.send(b"Login Sucsessful")
                    self.shell(sock, usr)
                
                else:
                    sleep("2")
                    sock.send(b"Wrong Login")
                    sock.close()
                    self.controll_client[i].close()
                    self.controll_activ[i] = False

                sock.close()
                self.controll_client[i].close()
                self.controll_activ[i] = False

        else:
            print("Connection lost to Client",i)
            self.controll_activ[i] = False

    def stop(self):
        self.controll_sock.close()
        self.controll_sock_d.close()
        print("Controll-Port: closed")
        self.data_sock.close()
        self.data_sock_d.close()
        print("Data-Port: closed")
s = Server()
try:
    while s.mode:
        pass
except:
    pass
s.stop
exit()
