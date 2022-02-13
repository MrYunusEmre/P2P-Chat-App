import socket
from threading import Thread
import datetime,time
import logging

logging.basicConfig(handlers=[logging.FileHandler('p2p.log', 'w', 'utf-8')], level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

#this thread control for online table and if user don't send hello and delete online table
class ServerUdp(Thread):
    def __init__(self, serverTCP):
        Thread.__init__(self)
        self.activeTimeList = []
        self.serverTCP = serverTCP
    def run(self):

        UDP_IP = socket.gethostbyname(socket.gethostname())
        UDP_PORT = 12346
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((UDP_IP, UDP_PORT))

        time_count = Thread(target=self.control,args=())
        time_count.start()

        while True:
            data, addr = sock.recvfrom(1024) # yeni birisi düstügü anda yakalıyor
            #print("Got udp connection from : ", addr)
            logging.info("SERVER - Got udp connection from : ", addr)

            newData = ""
            try:
                newData = data.decode().split('_')
            except:
                pass
            if(len(newData[1]) > 0):
                flag = False
                for member in self.activeTimeList:
                    if(member["username"] == newData[1]):
                        flag = True
                        self.activeTimeList.remove(member)
                        self.activeTimeList.append({"username": newData[1],"addr":addr, "lastWorkTime": datetime.datetime.now()})#update
                        break
                if(flag == False):
                    self.activeTimeList.append({"username": newData[1],"addr":addr, "lastWorkTime": datetime.datetime.now()})#new item

    #this function conrol for time
    def control(self):
        while True:
            flag = False
            for member in self.activeTimeList:
                timer = member["lastWorkTime"]
                timer = datetime.datetime.now() - timer
                if(timer.seconds > 20):
                    print("This user is absent for 20 seconds : ", member["username"])
                    logging.info("SERVER - This user is absent for 6 seconds : ", member["username"])
                    flag = True

                    self.activeTimeList.remove(member)
                    self.serverTCP.update_active_status(member["username"], 0)
                    #time.sleep(4)

