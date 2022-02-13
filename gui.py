import socket
import threading
from socket import error as socket_error
import tkinter as tk
import tkinter.messagebox
from tkinter import *

import sys
import os
import ClientTCP

from threading import Thread

from clientUDP import ClientUdp



LARGEFONT = ("Verdana", 35)
MEDIUMFONT = {"Verdana",15}

BG_GRAY = "#ABB289"
BG_COLOR = "#17202A"
TEXT_COLOR = "#EAECEE"

FONT = "Helvetica 14"
FONT_BOLD = "Helvetica 13 bold"


class GuiThread(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        self.app = TkinterApp()
        self.app.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.app.mainloop()

    def on_closing(self):
        if tkinter.messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.app.destroy()
            message = "LOGOUT" + "_" + self.app.username
            self.app.chatClient.setMessage(message)

class TkinterApp(tk.Tk):
    # __init__ function for class tkinterApp
    def __init__(self, *args, **kwargs):
        # this initiliaze new client object
        # __init__ function for class Tk
        tk.Tk.__init__(self, *args, **kwargs)
        for key,value in kwargs.items():
            if(key == "cli"):
                self.cli = value
                break
        self.username = ""
        self.messageTo = ""
        self.clientUdp = None
        self.client_socket = None
        self.flag = False
        # creating a container
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # initializing frames to an empty array
        self.frames = {}

        # iterating through a tuple consisting
        # of the different page layouts
        for F in (LoginPage, RegisterPage, SearchMenu):
            frame = F(container, self)

            # initializing frame of that object from
            # startpage, page1, page2 respectively with
            # for loop
            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(LoginPage)

        self.chatClient = None


    # to display the current frame passed as
    # parameter
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

    def show_page(self,index):
        if(index == 1):
            self.show_frame(LoginPage)
        elif(index == 2):
            self.show_frame(SearchMenu)



# first window frame startpage

class LoginPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        # label of frame Layout 2
        label = Label(self, text="Chat App", font=LARGEFONT)

        # putting the grid in its place by using
        # grid
        label.grid(row=0, column=4, padx=10, pady=10)

        # username label and text entry box
        usernameLabel = Label(self, text="User Name").grid(row=1, column=3)
        username = StringVar()
        usernameEntry = Entry(self, textvariable=username).grid(row=1, column=4)

        # password label and password entry box
        passwordLabel = Label(self, text="Password").grid(row=2, column=3)
        password = StringVar()
        passwordEntry = Entry(self, textvariable=password, show='*').grid(row=2, column=4)



        button_login = Button(self,text='Sign in',
                              command=lambda :self.login_user(controller,username, password)) # this will be redirected

        button_login.grid(row=3,column=4,padx=10,pady=10)

        button_sign_up = Button(self, text="Sign Up",
                             command=lambda: controller.show_frame(RegisterPage))

        # putting the button in its place by
        # using grid
        button_sign_up.grid(row=4, column=4, padx=10, pady=10)

    def login_user(self,controller,username,password):

        if(controller.chatClient == None):
            client = ClientTCP.ChatClient(username.get(),controller)
            client.start()
            controller.chatClient = client

        message = "LOGIN" + "_" + username.get() + "_" + password.get()
        controller.chatClient.setMessage(message)

# second window frame page1
class RegisterPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = Label(self, text="Sign Up", font=LARGEFONT)
        label.grid(row=0, column=4, padx=10, pady=10)

        # username label and text entry box
        usernameLabel = Label(self, text="User Name").grid(row=1, column=3)
        username = StringVar()
        usernameEntry = Entry(self, textvariable=username).grid(row=1, column=4)

        # password label and password entry box
        passwordLabel = Label(self, text="Password").grid(row=2, column=3)
        password = StringVar()
        passwordEntry = Entry(self, textvariable=password, show='*').grid(row=2, column=4)

        button_register = Button(self, text='Sign up',
                              command=lambda: self.register_client(controller, username, password))  # this will be redirected

        # putting the button in its place
        # by using grid
        button_register.grid(row=3, column=4, padx=10, pady=10)

    def register_client(self,controller, username, password):

        client = ClientTCP.ChatClient(username.get(),controller)
        client.start()
        controller.chatClient = client
        message = "REGISTER" + "_" + username.get() + "_" + password.get()
        client.setMessage(message)

class SearchMenu(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        controller.title("CHATAPP")

        label = Label(self, text="Welcome " + controller.username, font=MEDIUMFONT)
        label.grid(row=0, column=4,padx=15,pady=15)

        usernameLabel = Label(self, text="Search User : ").grid(row=1, column=3)
        username = StringVar()
        usernameEntry = Entry(self, textvariable=username).grid(row=1, column=4)
        button_search = Button(self, text='Search',
                              command=lambda:self.search_user(controller,username.get()))  # this will be redirected
        button_search.grid(row=1, column=5)

        button_logout = Button(self, text='Logout',
                               command=lambda:self.logout(controller))  # this will be redirected
        button_logout.grid(row=4, column=5)



    def search_user(self,controller, username):
        if(controller.chatClient.availability == "False"):
            tkinter.messagebox.showerror("Error", "This is not allowed right now !!")
        elif(controller.username == username):
            tkinter.messagebox.showerror("Error", "You should not search for yourself")
        else:
            message = "SEARCH" + "_" + controller.username + "_" + username #search_Ben_aradigimUser
            controller.chatClient.setMessage(message)

    def logout(self,controller):
        answer = tkinter.messagebox.askyesno("Logout", "Do you really want to logout ? ")
        if (not answer):
            return
        message = "LOGOUT" + "_" + controller.username
        controller.chatClient.setMessage(message)




class ChatPage(Thread):

    def __init__(self,client,messageTo,currentUser):
        Thread.__init__(self)
        self.client = client
        self.messageTo = messageTo
        self.currentUser = currentUser
        self.response = ""

    def run(self):

        self.window = Tk()

        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        self._setup_main_window()
        self.window.mainloop()

    def _setup_main_window(self):
        self.window.title("Chat" + "_" )
        self.window.resizable(width=False, height=False)
        self.window.configure(width=470, height=550, bg=BG_COLOR)

        head_label = Label(self.window,bg=BG_COLOR, fg=TEXT_COLOR, text="Welcome", font=FONT_BOLD, pady=10)

        head_label.place(relwidth=1)

        line = Label(self.window,width=450, bg=BG_GRAY)
        line.place(relwidth=1, rely= 0.07, relheight=0.012)

        self.text_widget = Text(self.window, width=20, height=2, bg=BG_COLOR,fg=TEXT_COLOR, font=FONT,padx=5,pady=5)

        self.text_widget.place(relheight=0.745, relwidth=1, rely= 0.08)
        self.text_widget.configure(cursor="arrow", state= DISABLED)

        scrollbar = Scrollbar(self.text_widget)
        scrollbar.place(relwidth=1, relx=0.974)
        scrollbar.configure(command=self.text_widget)

        bottom_label = Label(self.window,bg=BG_GRAY,height=80)
        bottom_label.place(relwidth=1, rely=0.825)

        self.msg_entry = Entry(bottom_label,bg="#2C3E50",fg=TEXT_COLOR,font=FONT)
        self.msg_entry.place(relwidth=0.74, relheight=0.06,rely=0.008,relx=0.011)
        self.msg_entry.focus()
        self.msg_entry.bind("<Return>",self._on_enter_pressed)

        send_button = Button(bottom_label, text="Send", font=FONT_BOLD,width=20,bg=BG_GRAY,
                             command=lambda:self._on_enter_pressed(None))
        send_button.place(relx=0.77, rely=0.008, relheight=0.06, relwidth=0.022)


    def _on_enter_pressed(self,event):
        msg = self.msg_entry.get()
        self._insert_message(msg, self.client.nickname)

        users = ""
        for member in self.messageTo:
            users += member + "_"
        users = users[:-1]
        #print("mesaj giden userlar : " + users)
        #print("Giden mesaj from gui : " + "MESSAGE"+"_"+users+"_"+self.client.nickname+"_"+msg)
        self.client.setMessage("MESSAGE"+"_"+users+"_"+self.client.nickname+"_"+msg) #message_messageTo_messageFrom_messageContent


    def _insert_message(self,msg,sender):
        if not msg:
            return

        self.msg_entry.delete(0,END)
        msg1 = f"{sender}: {msg}\n\n"
        self.text_widget.configure(state=NORMAL)
        self.text_widget.insert(END, msg1)
        self.text_widget.configure(state=DISABLED)

        self.text_widget.see(END)

    def on_closing(self):
        if tkinter.messagebox.askokcancel("Quit", f"Do you want to close chat ?"):
            self.client.availability = "True"
            #message = "SETAVAILABILITY" + "_" + self.messageTo
            #self.client.setMessage(message)
            self.window.destroy()

    def get_message_to(self):
        return self.messageTo

    def update_message_to(self,messageTo):
        self.messageTo = messageTo


def main():

    thr = GuiThread()
    thr.start()

if __name__ == '__main__':
    main()