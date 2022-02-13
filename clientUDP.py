from threading import Thread
import time
import socket


#this thread class send hello message and user go on online
class ClientUdp(Thread):
    def __init__(self,logout,username):
        Thread.__init__(self)
        self.logout = logout
        self.username = username

    def run(self):
        try:
            UDP_IP = socket.gethostbyname(socket.gethostname())
            UDP_PORT = 12346
            MESSAGE = "HELLO" + "_" + self.username
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.connect((UDP_IP, UDP_PORT))
        except:
            print("clientUDP kısmında baglantı kurarken hata meydana geldi")



        while not self.logout:
            sock.send(MESSAGE.encode())
            #print(UDP_IP, MESSAGE)
            time.sleep(6)

        sock.close()
