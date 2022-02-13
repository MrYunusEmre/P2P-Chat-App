# Import socket module
import socket
import threading
import tkinter.messagebox
from threading import Thread
import clientUDP
import gui
import logging

logging.basicConfig(handlers=[logging.FileHandler('p2p.log', 'w', 'utf-8')], level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

class ChatClient(Thread):
    def __init__(self,username,controller):
        Thread.__init__(self)

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = socket.gethostbyname(socket.gethostname())
        self.port = 55555
        self.client.connect((self.host,self.port))
        self.nickname = username
        logging.info(f"CLIENT - Client is started.... HOST: {self.host} PORT: {self.port} ")
        self.chat = None
        self.availability = "True"

        self.controller = controller
        self.message = ""

        self.gui_thread = None
        self.messageTo = []

        self.receive_thread = threading.Thread(target=self.receive)
        self.receive_thread.start()

        self.write_thread = threading.Thread(target=self.write)
        self.write_thread.start()

    def receive(self):
        while True:
            try:
                message = self.client.recv(1024).decode('utf-8')
                #print(message)
                logging.info("CLIENT - Message: " + message)
                if(message == "NICK"):
                    self.client.send(self.nickname.encode('utf-8'))
                else:
                    newMessage = message.split("_")
                    if(newMessage[0] == "REGISTERED"):
                        try:
                            logging.info("CLIENT - " + f"User: {self.nickname} registered")
                            self.controller.show_page(1)
                        except:
                            print("Page degisirken hata")

                    elif(newMessage[0] == "LOGIN"):
                        try:
                            logging.info("CLIENT - " + f"User: {self.nickname} logged in")
                            self.controller.show_page(2)
                            self.controller.username = newMessage[1]

                            gui_thread = threading.Thread(target=self.run_udp_client(), args=())
                            gui_thread.start()

                        except:
                            print("Login page'e gecilirken hata")

                    elif(newMessage[0] == "LOGOUT"):
                        logging.info("CLIENT - " + f"User: {self.nickname} logged out")
                        self.udp_client.logout = True
                        self.controller.show_page(1)

                    elif(newMessage[0] == "FOUND"):
                        try:
                            logging.info("CLIENT - " + f"User: {self.nickname} is asked for chat with {newMessage[1]}")
                            ans = tkinter.messagebox.askyesno("USER", f"Do you want to chat with user: {newMessage[1]}")

                            if(ans == True):
                                message = "CHAT" + "_" + newMessage[1] + "_" + newMessage[2]
                                self.setMessage(message)

                        except:
                            print()

                    elif(newMessage[0] == "NOTFOUND"):
                        tkinter.messagebox.showerror("ERROR", "User is not online or existed !!")

                    elif(newMessage[0] == "CHATREQUEST"):

                        if(self.availability == "False"):
                            logging.info("CLIENT - " + f"User: {self.nickname} sent BUSY message to the server")
                            message = "BUSY" + "_" + newMessage[1] + "_" + newMessage[2]
                            self.setMessage(message)
                        else:
                            logging.info("CLIENT - " + f"User: {self.nickname} is asked for chat request with {newMessage[1]}")
                            ans = tkinter.messagebox.askyesno("Chat Request", f"Do you want to chat with user: {newMessage[1]}")

                            if(ans == True):
                                logging.info("CLIENT - " + f"User: {self.nickname} accepted chat request")
                                message = "OK" + "_" + newMessage[1] + "_" + newMessage[2]
                                self.setMessage(message)
                            elif(ans == False):
                                logging.info("CLIENT - " + f"User: {self.nickname} rejected chat request")
                                message = "REJECT" + "_" + newMessage[1]
                                self.setMessage(message)

                    elif(newMessage[0] == "STARTCHAT"):
                        logging.info("CLIENT - " + f"Chat started for User: {self.nickname}")
                        self.availability = "False"
                        self.messageTo.append(newMessage[1])
                        self.gui_thread = threading.Thread(target=self.run_gui_chat_page, args=(self.messageTo,))
                        self.gui_thread.start()

                    elif(newMessage[0] == "SETAVAILABILITY"):
                        self.availability = "True"

                    elif(newMessage[0] == "REJECT"):
                        tkinter.messagebox.showerror("ERROR","User rejected your chat request :( ..")

                    elif(newMessage[0] == "BUSY"):
                        if tkinter.messagebox.askyesno("Group Chat Request", "User is chatting with someone else. Do you want to join ?"):
                            logging.info("CLIENT - " + f"User: {self.nickname} sent request to join group chat")
                            message = "GROUPCHATREQUEST" + "_" + newMessage[1] + "_" + newMessage[2]
                            self.setMessage(message)
                        # tkinter.messagebox.showerror("ERROR","User has been chatting with someone else :( ..")

                    elif(newMessage[0] == "GROUPCHATREQUEST"):
                        if tkinter.messagebox.askyesno("Coming Chat Request",f"user: {newMessage[1]} wants to join your chat. What do you think?"):
                            logging.info("CLIENT - " + f"User: {self.nickname} acceppted join request of {newMessage[1]}")
                            message = "APPROVEGROUPCHATREQUEST" + "_" + newMessage[1] + "_" + newMessage[2]
                            self.setMessage(message)
                        else:
                            logging.info("CLIENT - " + f"User: {self.nickname} declined join request of {newMessage[1]}")
                            message = "DECLINEGROUPCHATREQUEST" + "_" + newMessage[1] + "_" + newMessage[2]
                            self.setMessage(message)

                    elif(newMessage[0] == "DECLINEGROUPCHATREQUEST"):
                        logging.info("CLIENT - " + f"User: {self.nickname} got rejected of joining chat group")
                        tkinter.messagebox.showerror("Rejected", "Your join request is rejected.")

                    elif(newMessage[0] == "APPROVEGROUPCHATREQUEST"):
                        logging.info("CLIENT - " + f"User: {self.nickname} got accepted of joining chat group")
                        #print("messageTo : " + newMessage[2])
                        self.messageTo.append(newMessage[2])

                        message = "UPDATEMESSAGETO" + "_" + self.nickname + "_" + newMessage[2]
                        self.setMessage(message)

                        self.availability = "False"
                        self.gui_thread = threading.Thread(target=self.run_gui_chat_page, args=(self.messageTo,))
                        self.gui_thread.start()

                    elif(newMessage[0] == "UPDATEMESSAGETO"):
                        #print("Anlık mesaj to : ")
                        #print(self.messageTo)
                        all_message_to = self.chat.get_message_to()

                        if(newMessage[1] not in self.messageTo):
                            self.messageTo.append(newMessage[1])
                        self.chat.update_message_to(self.messageTo)     #ilk irtibata geçtigimiz kullanıcıya yeni geleni ekledk
                        #print(self.messageTo)


                        all_users_str = ""

                        for user in all_message_to:
                            all_users_str += user + "_"
                        all_users_str = all_users_str[:-1]

                        message = "UPDATEALLUSERSMESSAGETO" + "_" + all_users_str + "_" + newMessage[1]
                        self.setMessage(message)

                    elif(newMessage[0] == "UPDATEALLUSERSMESSAGETO"):
                        if(newMessage[1] not in self.messageTo):
                            self.messageTo.append(newMessage[1])
                        self.chat.update_message_to(self.messageTo)

                    elif(newMessage[0] == "UPDATELASTADDEDONEMESSAGETO"):
                        users = newMessage[1:]
                        for user in users:
                            self.messageTo.append(user)
                        self.chat.update_message_to(self.messageTo)

                    elif(newMessage[0] == "REGISTERERROR"):
                        logging.info("CLIENT - " + f"Username: {self.nickname} has already taken by someone else!!")
                        tkinter.messagebox.showerror("ERROR","Please change the username and try again !!")

                    elif(newMessage[0] == "LOGINERROR"):
                        tkinter.messagebox.showerror("ERROR","Please check the user credentials !!")

                    elif(newMessage[0] == "ALREADYLOGINERROR"):
                        tkinter.messagebox.showerror("ERROR", "This user has already logged in !!")

                    elif(newMessage[0] == "MESSAGE"):
                        self.chat._insert_message(newMessage[2],newMessage[1])

            except:
                print("An error occured !!")
                self.client.close()
                break

    def write(self):
        while True:
            if(self.message != ""):
                self.client.send(self.message.encode('utf-8'))
                self.message = ""
            else:
                pass

    def setMessage(self,message):
        self.message = message

    def run_gui_chat_page(self,messageTo):
        self.chat = gui.ChatPage(self, messageTo,self.nickname)
        self.chat.start()

    def run_udp_client(self):
        self.udp_client = clientUDP.ClientUdp(False,self.nickname)
        self.udp_client.start()


def main():
    chatClient = ChatClient(None,None)
    chatClient.start()

if __name__ == '__main__':
    main()
