#Juho Jääskeläinen 6.3.2022
import tkinter as tk
from tkinter import scrolledtext
from tkinter import messagebox

from xmlrpc.client import ServerProxy

###FOR THE GUI
BLACK = "black"
WHITE='white'
FONT = ("Helvetica", 17)
FONT_TITTLE=("Helvetica bold",20,)
BUTTON_FONT = ("Helvetica", 15)
SMALL_FONT = ("Helvetica", 13)

BG_BLUE='#4472C4'
BT_GREEN='#70AD47'

class GUI: ##Handles the GUI
    ip_address=None
    client=None
    CW=None
    def __init__(self,master):#Iniatez the first window for showing and looking for the database
        self.master=master
        self.master.geometry("1280x720")
        self.master.title("My Wiki")
        self.master.resizable(False,False)
        self.master.configure(bg=BG_BLUE)

        self.frame=tk.Frame(self.master,bg=BG_BLUE)

        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_rowconfigure(1, weight=1)
        self.frame.grid_rowconfigure(2, weight=8)

        self.topic_frame=tk.Frame(self.frame,width=1280,height=256,bg=BG_BLUE)
        self.topic_frame.grid(row=0,column=1,sticky=tk.NSEW)

        self.title_frame=tk.Frame(self.frame,width=1280,height=256,bg=BG_BLUE)
        self.title_frame.grid(row=1,column=1,sticky=tk.NSEW)

        self.text_frame=tk.Frame(self.frame,width=1280,height=1024,bg=BG_BLUE)
        self.text_frame.grid(row=2,columnspan=2,sticky=tk.NSEW)

        self.topic_textbox=tk.Entry(self.topic_frame,font=FONT, bg=WHITE, fg='gray', width=38)#Tähän default text?
        self.topic_textbox.insert(0,'Topic')
        self.topic_textbox.bind("<FocusIn>", self.handle_focus_in_topic)
        self.topic_textbox.bind("<FocusOut>", self.handle_focus_out_topic)
        self.topic_textbox.pack(side=tk.LEFT)
        self.button_search=tk.Button(self.topic_frame,text='Search',font=BUTTON_FONT, bg=BT_GREEN, fg=BLACK, command=self.search)
        self.button_search.pack(side=tk.LEFT)
        self.button_add=tk.Button(self.topic_frame,text='Add', font=BUTTON_FONT, bg=BT_GREEN, fg=BLACK, command=self.add)
        self.button_add.pack(side=tk.LEFT)

        self.title_textbox=tk.Entry(self.title_frame,font=FONT, bg=WHITE, fg=BLACK, width=38)
        self.title_textbox.insert(tk.END,'Tittle')
        self.title_textbox.pack(side=tk.LEFT)
        self.button_submit=tk.Button(self.title_frame,text='Submit',font=BUTTON_FONT,bg=BT_GREEN,fg=BLACK,command=self.submit)
        self.button_submit.pack(side=tk.LEFT)

        self.text_box=scrolledtext.ScrolledText(self.text_frame,font=SMALL_FONT,bg=WHITE,fg=BLACK,width=139,height=33)
        self.text_box.tag_config("bold",font=FONT_TITTLE)
        self.text_box.pack(fill='both',expand=True)
        self.text_box.configure(state=tk.DISABLED)
        self.frame.pack()
        self.title_frame.grid_remove()#hides the title frame

    def show_results(self,notebook):
        #Shows the results from the server in text_box with some styling so that note title is bolded and bigger
        self.text_box.configure(state=tk.NORMAL)#Cleans the text box
        self.topic_textbox.delete(0, tk.END)
        self.text_box.delete("1.0","end")
        if notebook!='Not found':
            self.topic_textbox.insert(tk.END, notebook['topic'])#Deletes the topic and puts capitalization right.
            ##Itterates over the notes
            for note in notebook.keys():#Parses the data from server and displays it.
                if note!='topic':#Skips first dict that is the topic
                    noteTitle=notebook[note]['note']
                    text=notebook[note]['text']
                    timestampString=notebook[note]['timestamp']
                    #print(noteTitle+'::'+text+'::'+timestampString)
                    self.text_box.insert(tk.END, noteTitle+'\n','bold')
                    self.text_box.insert(tk.END, '\n'+timestampString+'\n')
                    self.text_box.insert(tk.END, text+'\n\n')

        else:#Server should always return something, but just in case.
            self.text_box.insert(tk.END,notebook+' Something went wrong')

        self.text_box.configure(state=tk.DISABLED)



    def search(self):
        #Handles search request to the server
        self.button_add.config(state=tk.NORMAL)
        print('searching database')
        if self.topic_textbox.get()!='':#Default behavior is that if the topic is empty nothing happens
            note = API_methods.get_note(self.topic_textbox.get())
            self.show_results(note)



    def add(self):
        #Disable add button and open new window
        self.button_add.config(state=tk.DISABLED)
        self.write_note()
        print('Switching to adding mode')

    def submit(self,topic,title,text):#Sends data to server, and then shows the updated notebook
        print('submitting')
        #print(topic,title,text)
        succesful=API_methods.add_note(topic,title,text)
        return succesful


    def enable_add_button(self):
        self.button_add.config(state=tk.NORMAL)

    #Logic to handle the topic input fields autofill and gray out
    def handle_focus_in_topic(self,_):
        if self.topic_textbox.get()=='Topic':
            self.topic_textbox.delete(0, tk.END)
            self.topic_textbox.config(fg='black')

    def handle_focus_out_topic(self,_):
        if self.topic_textbox.get()=='':
            self.topic_textbox.delete(0, tk.END)
            self.topic_textbox.config(fg='grey')
            self.topic_textbox.insert(0, "Topic")
##################second GUI#####################################
    def write_note(self):#Opens new window for writingt new note.
        def on_closing():
            if messagebox.askokcancel("Quit", "Do you want to stop adding new note?"):
                self.enable_add_button()
                top.destroy()

        def submit_check(topic,title,text):#Handless the submission to server
            if topic.strip()=='' or title.strip()=='' or text.strip() == '':
                messagebox.showerror('Error','Topic, title or text is empty')
            else:
                succesful = self.submit(topic,title,text)
                print(succesful)
                if succesful==201:#If submission worked then closes window and shows the notebook for that topic.
                    self.topic_textbox.delete(0, tk.END)
                    self.topic_textbox.insert(0, topic)
                    self.search()
                    top.destroy()



        top= tk.Toplevel(self.master)
        top.geometry("1280x720")
        top.title("My Wiki")
        top.protocol("WM_DELETE_WINDOW", on_closing)

        writeFrame=tk.Frame(top,bg=BG_BLUE)
        writeFrame.grid_rowconfigure(0, weight=1)
        writeFrame.grid_rowconfigure(1, weight=1)
        writeFrame.grid_rowconfigure(2, weight=8)

        topic_frame=tk.Frame(writeFrame,width=1280,height=256,bg=BG_BLUE)
        topic_frame.grid(row=0,column=1,sticky=tk.NSEW)

        title_frame=tk.Frame(writeFrame,width=1280,height=256,bg=BG_BLUE)
        title_frame.grid(row=1,column=1,sticky=tk.NSEW)

        text_frame=tk.Frame(writeFrame,width=1280,height=1024,bg=BG_BLUE)
        text_frame.grid(row=2,columnspan=2,sticky=tk.NSEW)

        topic_textbox=tk.Entry(topic_frame,font=FONT, bg=WHITE, fg=BLACK, width=38)#Tähän default text?
        topic_textbox.insert(0,'Topic')
        topic_textbox.bind("<FocusIn>", self.handle_focus_in_topic)#Needs to be made in this method
        topic_textbox.bind("<FocusOut>", self.handle_focus_out_topic)
        topic_textbox.pack(side=tk.LEFT)


        title_textbox=tk.Entry(title_frame,font=FONT, bg=WHITE, fg=BLACK, width=38)
        title_textbox.insert(tk.END,'Tittle')
        title_textbox.pack(side=tk.LEFT)
        button_submit=tk.Button(title_frame,text='Submit',font=BUTTON_FONT,bg=BT_GREEN,fg=BLACK,command=lambda: submit_check(topic_textbox.get(),title_textbox.get(),text_box.get("1.0",'end-1c')))
        button_submit.pack(side=tk.LEFT)

        text_box=scrolledtext.ScrolledText(text_frame,font=SMALL_FONT,bg=WHITE,fg=BLACK,width=139,height=33)
        text_box.tag_config("bold",font=FONT_TITTLE)
        text_box.pack(fill='both',expand=True)
        writeFrame.pack()

class API_methods:#Offers methods to handle server communications
    @staticmethod
    def get_note(topic):
        #print(f'{topic}')
        proxy=ServerProxy('http://localhost:3000')
        note=proxy.GET_note(f'{topic}')
        return note

    @staticmethod
    def add_note(topic,title,note):
        proxy=ServerProxy('http://localhost:3000')
        message_recived=proxy.PUT_note(topic,title,note)
        return message_recived



def main():
    root = tk.Tk()
    connect = GUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
