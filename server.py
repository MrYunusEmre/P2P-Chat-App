import socket
import threading
from threading import Thread
from serverUDP import ServerUdp
import logging

logging.basicConfig(handlers=[logging.FileHandler('p2p.log', 'w', 'utf-8')], level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

class ChatServer(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.host = socket.gethostbyname(socket.gethostname())
        self.port = 55555
        self.all_clients = []
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host,self.port))
        self.server.listen()

        print("Server is started.....")
        logging.info(f"SERVER - Server is started.... HOST: {self.host} PORT: {self.port} ")

        self.receive_thread = threading.Thread(target=self.receive)
        self.receive_thread.start()

    def broadcast(self,message,client):
        #print("MESAJJ : ", message)
        logging.info("SERVER - Coming Message => " + message)
        newMessage = message.split("_")

        if(newMessage[0] == "REGISTER"):
            self.register_user(newMessage,client)
            return
        elif(newMessage[0] == "LOGIN"):
            self.login_user(newMessage,client)
            return
        elif(newMessage[0] == "LOGOUT"):
            self.logout_user(newMessage,client)
            return
        elif(newMessage[0] == "SEARCH"):
            self.search_user(newMessage,client)
            return
        elif(newMessage[0] == "CHAT"):
            self.chat_request(newMessage,client)
            return
        elif(newMessage[0] == "OK"):
            self.start_chat(newMessage,client)
            return
        elif(newMessage[0] == "REJECT"):
            self.reject_request(newMessage,client)
            return
        elif(newMessage[0] == "BUSY"):
            self.decline_request(newMessage,client)
            return
        elif(newMessage[0] == "MESSAGE"):
            self.set_message(newMessage,client)
            return
        elif(newMessage[0] == "SETAVAILABILITY"):
            self.set_availability(newMessage,client)
            return
        elif(newMessage[0] == "GROUPCHATREQUEST"):
            self.send_group_chat_request(newMessage,client)
            return
        elif(newMessage[0] == "APPROVEGROUPCHATREQUEST"):
            self.approve_group_chat_request(newMessage,client)
            return
        elif(newMessage[0] == "DECLINEGROUPCHATREQUEST"):
            self.decline_group_chat_request(newMessage,client)
            return
        elif(newMessage[0] == "UPDATEMESSAGETO"):
            self.update_message_to(newMessage,client)
            return
        elif(newMessage[0] == "UPDATEALLUSERSMESSAGETO"):
            self.update_all_users_message_to(newMessage,client)
            return

    def handle(self,client):
        while True:
            try:
                message = client.recv(1024).decode('utf-8')
                if(len(message) > 2):
                    self.broadcast(message,client)
            except:
                # print("HATA in the handle method")
                break

    def receive(self):
        while True:
            client, address = self.server.accept()
            print(f"Connected with {str(address)}")
            logging.info("SERVER - " + f"Connected with {str(address)}")
            client.send("Connected to the server!".encode('utf-8'))

            self.handle_thread = threading.Thread(target=self.handle, args=(client,))
            self.handle_thread.start()

    def register_user(self,newMessage,client):

        for member in self.all_clients:
            if(member["username"] == newMessage[1]): #Check for user existence
                message = "REGISTERERROR"
                client.send(message.encode("utf-8"))
                return

        self.all_clients.append({"username":newMessage[1], "password":newMessage[2], "active":0, "client":client})
        #print(f"user : {newMessage[1]} is successfully registered to the server.")
        logging.info("SERVER - " + f"user : {newMessage[1]} is successfully registered to the server.")
        client.send("REGISTERED".encode("utf-8"))

    def login_user(self,newMessage,client):

        for member in self.all_clients:
            if(member["username"] == newMessage[1] and member["password"] == newMessage[2] and member["active"] == 0):
                logging.info("SERVER - " f"User: {newMessage[1]} is logged in.")
                member["active"] = 1
                message = "LOGIN" + "_" + newMessage[1]
                client.send(message.encode("utf-8"))
                return
            elif(member["username"] == newMessage[1] and member["password"] == newMessage[2] and member["active"] == 1):
                logging.info("SERVER - ERROR - " f"User: {newMessage[1]} is already logged in.!!")
                message = "ALREADYLOGINERROR"
                client.send(message.encode("utf-8"))
                return
        logging.info("SERVER - ERROR - " f"Credentials are wrong... Username: {newMessage[1]} , Password: {newMessage[2]}!!")
        message = "LOGINERROR"
        client.send(message.encode("utf-8"))

    def logout_user(self,newMessage,client):

        for member in self.all_clients:
            if(member["username"] == newMessage[1]):
                member["active"] = 0
                break
        logging.info("SERVER - " + f"User: {newMessage[1]} is successfully logged out.")
        message = "LOGOUT"
        client.send(message.encode("utf-8"))

    def search_user(self,newMessage,client):

        for member in self.all_clients:
            if(member["username"] == newMessage[2]):
                logging.info("SERVER - " + f"User : {newMessage[1]} searchs for User: {newMessage[2]} Result-> FOUND")
                message = "FOUND" + "_" + member["username"] + "_" + newMessage[1] #newMessage[1] = o anki user
                client.send(message.encode("utf-8"))
                return
        message = "NOTFOUND"
        client.send(message.encode("utf-8"))

    def chat_request(self,newMessage,client):

        for member in self.all_clients:
            if(member["username"] == newMessage[1]):
                logging.info("SERVER - " + f"User: {newMessage[2]} sent chat request to {newMessage[1]}")
                message = "CHATREQUEST" + "_" + newMessage[2] + "_" + newMessage[1]
                member["client"].send(message.encode("utf-8"))
                break

    def reject_request(self,newMessage,client):

        for member in self.all_clients:
            if(member["username"] == newMessage[1]):
                logging.info("SERVER - " + f"User: {newMessage[1]} rejected the chat request")
                message = "REJECT"
                member["client"].send(message.encode("utf-8"))
                break

    def decline_request(self,newMessage,client):

        for member in self.all_clients:
            if(member["username"] == newMessage[1]):
                logging.info("SERVER - " + f"User: {newMessage[1]} is BUSY")
                message = "BUSY" + "_" + newMessage[1] + "_" + newMessage[2]
                member["client"].send(message.encode("utf-8"))
                break

    def start_chat(self,newMessage,client):
        logging.info("SERVER - " + f"Chat started.. Users : {newMessage[1]} , {newMessage[2]}")
        for member in self.all_clients:
            if(member["username"] == newMessage[1]):
                message = "STARTCHAT" + "_" + newMessage[2]
                member["client"].send(message.encode("utf-8"))
            elif(member["username"] == newMessage[2]):
                message = "STARTCHAT" + "_" + newMessage[1]
                member["client"].send(message.encode("utf-8"))

    def set_message(self,newMessage,client):
        #print(newMessage)
        size = len(newMessage)
        msg = newMessage[size-1]
        sender = newMessage[size-2]
        receivers = newMessage[1:size-2]
        #print(receivers)

        for member in self.all_clients:
            if(member["username"] in receivers):
                #print("User found to send a messageeee")
                logging.info("SERVER - " + f"Message: {newMessage[size-1]} From: {newMessage[size-2]} To: {member['username']} ")
                message = "MESSAGE" + "_" + newMessage[size-2] + "_" + newMessage[size-1]
                member["client"].send(message.encode('utf-8'))

    def update_active_status(self,username,value):

        for member in self.all_clients:
            if(member["username"] == username):
                member["active"] = value
                break

    def set_availability(self,newMessage,client):

        for member in self.all_clients:
            if(member["username"] == newMessage[1]):
                logging.info("SERVER - " + f"User: {newMessage[1]}'s availability is arranged")
                message = "SETAVAILABILITY"
                member["client"].send(message.encode("utf-8"))
                break

    def send_group_chat_request(self,newMessage,client):

        for member in self.all_clients:
            if(member["username"] == newMessage[2]):
                logging.info("SERVER - " + f"Group chat request is sent to {newMessage[2]}")
                message = "GROUPCHATREQUEST" "_" + newMessage[1] + "_" + newMessage[2]
                member["client"].send(message.encode("utf-8"))
                break

    def approve_group_chat_request(self,newMessage,client):

        for member in self.all_clients:
            if(member["username"] == newMessage[1]):
                logging.info("SERVER - " + f"Group chat request is approved by {newMessage[1]}")
                message = "APPROVEGROUPCHATREQUEST" + "_" + newMessage[1] + "_" + newMessage[2]
                member["client"].send(message.encode("utf-8"))
                break

    def decline_group_chat_request(self,newMessage,client):

        for member in self.all_clients:
            if(member["username"] == newMessage[1]):
                message = "DECLINEGROUPCHATREQUEST"
                member["client"].send(message.encode("utf-8"))
                break

    def update_message_to(self,newMessage,client):

       #print(newMessage)
        user_list = newMessage[2:]
        #print(user_list)
        for member in self.all_clients:
            if(member["username"] in user_list):
                message = "UPDATEMESSAGETO" + "_" + newMessage[1]
                member["client"].send(message.encode("utf-8"))

    def update_all_users_message_to(self,newMessage,client):
        last_added = newMessage[len(newMessage)-1]
        str_others = ""
        temp_member = None
        for member in self.all_clients:
            if(member["username"] != last_added):
                str_others += member["username"] + "_"
                message = "UPDATEALLUSERSMESSAGETO" + "_" + last_added
                member["client"].send(message.encode("utf-8"))
            else:
                temp_member = member
        str_others = str_others[:-1]
        message = "UPDATELASTADDEDONEMESSAGETO" + "_" + str_others
        temp_member["client"].send(message.encode("utf-8"))

def main():
    chatServer = ChatServer()
    chatServer.start()
    serverUdp = ServerUdp(chatServer)
    serverUdp.start()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    #gui.main()
    main()
