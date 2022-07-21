#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import sys
from unicodedata import name
import numpy as np
import librosa
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.models import load_model
from werkzeug.utils import secure_filename
import threading
import time
import tkinter.messagebox
from tkinter import *
from tkinter import filedialog
from tkinter import ttk
from ttkthemes import themed_tk as tk
from mutagen.mp3 import MP3
from pygame import mixer
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg as fg


# In[2]:


model=load_model('model')


# In[3]:


labelencoder = LabelEncoder()
labelencoder.fit_transform(['Airplane', 'Bics', 'Cars', 'Helicopter', 'Motocycles', 'Train', 'Truck', 'bus'])


# In[4]:


def typevicule():
    path='C:\\Users\\PC\\Downloads\\Image-vehicule\\'
    selected_song = playlistbox.curselection()
    selected_song = int(selected_song[0])
    play_it = playlist[selected_song]
    audio, sample_rate = librosa.load(play_it, res_type='kaiser_fast', duration=5)
    mfccs_features = librosa.feature.mfcc(y=audio, sr=sample_rate, n_mfcc=80)
    mfccs_scaled_features = np.mean(mfccs_features.T, axis=0)
    pre=mfccs_scaled_features.reshape(1,1,80)
    prediction = model.predict(pre)
    classes_x = np.argmax(prediction, axis=1)
    prediction_class = labelencoder.inverse_transform(classes_x)
    global stopPhot
    stopPhot = PhotoImage(file=path+str(prediction_class[0])+'.png').subsample(3,4)
    stopBt = tkinter.Label(row2,image=stopPhot,borderwidth=0,relief="ridge",bg="brown")
    stopBt.grid(row=0, column=5)


# In[5]:


def graph():
        selected_song = playlistbox.curselection()
        selected_song = int(selected_song[0])
        play_it = playlist[selected_song]
        song,sample_rate = librosa.load(play_it, sr = None)
        figure=plt.figure()
        figure.add_subplot(111).plot(np.linspace(0, 2, num=len(song)),song)
        plt.xlabel("Time")
        plt.ylabel("Amplitude")
        chart=fg(figure,rigframe)
        chart.get_tk_widget().grid(row=1,column=3)


# In[6]:



root = tk.ThemedTk()
root.get_themes()                 # Returns a list of all themes that can be set
root.set_theme("radiance")



statusbar = ttk.Label(root, text="Welcome to vhicule identification", relief=SUNKEN, anchor=W, font='Times 10 italic')
#statusbar.pack(side=BOTTOM, fill=X)

# Create the menubar
menubar = Menu(root)
root.config(menu=menubar,background='black')

# Create the submenu

subMenu = Menu(menubar, tearoff=0)

playlist = []

# playlist - contains the full path + filename
# playlistbox - contains just the filename
# Fullpath + filename is required to play the music inside play_music load function
#open the browser to add the music
def browse_file():
    global filename_path
    filename_path = filedialog.askopenfilename()
    add_to_playlist(filename_path)
    mixer.music.queue(filename_path)


def add_to_playlist(filename):
    filename = os.path.basename(filename)
    index = 0
    playlistbox.insert(index, filename)
    playlist.insert(index, filename_path)
    index += 1


menubar.add_cascade(label="File", menu=subMenu)
subMenu.add_command(label="Open", command=browse_file)
subMenu.add_command(label="Exit", command=root.destroy)


def about_us():
    tkinter.messagebox.showinfo('About Application', 'Vehicle identification from sound')


subMenu = Menu(menubar, tearoff=0)
menubar.add_cascade(label="Help", menu=subMenu)
subMenu.add_command(label="About Us", command=about_us)

mixer.init()  # initializing the mixer

root.title("Vehicle identification")
root.iconbitmap(r'C:\\Users\\PC\\Downloads\\2.ico')

# Root Window - StatusBar, LeftFrame, RightFrame
# LeftFrame - The listbox (playlist)
# RightFrame - TopFrame,MiddleFrame and the BottomFrame

classframe=Frame(root,background='brown',padx=5,pady=5)
classframe.grid(row=0, column=0)
leftframe = Frame(classframe,background='brown',padx=10,pady=10)
leftframe.grid(row=0, column=0)
autre0=Frame(leftframe)
autre0.grid(row=0,column=0)
#plafr=Frame(leftframe)
playlistbox = Listbox(autre0,font=20,background="grey",borderwidth=10,width=50)
playlistbox.grid(row=0,column=0,ipadx=10,ipady=10,pady=10)

tajrba = Frame(classframe)
tajrba.grid(row=0, column=4)

autre1=Frame(leftframe,background='brown')
autre1.grid(row=1,column=0)

##############################
##############################

addBtn = tkinter.Button(autre1, text="+ Add",borderwidth=4,relief="groove",bg="green", command=browse_file)
addBtn.grid(row=0,column=0)


def del_song():
    selected_song = playlistbox.curselection()
    selected_song = int(selected_song[0])
    playlistbox.delete(selected_song)
    playlist.pop(selected_song)
delBtn = tkinter.Button(autre1, text="- Del",borderwidth=4,relief="groove",bg="red", command=del_song)
delBtn.grid(row=0,column=1)


rightframe = Frame(classframe,background="brown")
rightframe.grid(row=0,column=1,padx=50)

topframe = Frame(rightframe,bg="grey")
topframe.grid(row=0,column=0)

lengthlabel = tkinter.Label(topframe, text='Total Length : --:--',bg="grey")
lengthlabel.grid(row=0,column=0)

currenttimelabel =tkinter.Label(topframe, text='Current Time : --:--',bg="grey", relief=GROOVE)
currenttimelabel.grid(row=1,column=0)



def show_details(play_song):
    file_data = os.path.splitext(play_song)

    if file_data[1] == '.MP3':
        audio = MP3(play_song)
        total_length = audio.info.length
    else:
        a = mixer.Sound(play_song)
        total_length = a.get_length()

    # div - total_length/60, mod - total_length % 60
    mins, secs = divmod(total_length, 60)
    mins = round(mins)
    secs = round(secs)
    timeformat = '{:02d}:{:02d}'.format(mins, secs)
    lengthlabel['text'] = "Total Length" + ' - ' + timeformat

    t1 = threading.Thread(target=start_count, args=(total_length,))
    t1.start()


def start_count(t):
    global paused
    # mixer.music.get_busy(): - Returns FALSE when we press the stop button (music stop playing)
    # Continue - Ignores all of the statements below it. We check if music is paused or not.
    current_time = 0
    while current_time <= t and mixer.music.get_busy():
        if paused:
            continue
        else:
            mins, secs = divmod(current_time, 60)
            mins = round(mins)
            secs = round(secs)
            timeformat = '{:02d}:{:02d}'.format(mins, secs)
            currenttimelabel['text'] = "Current Time" + ' - ' + timeformat
            time.sleep(1)
            current_time += 1


def play_music():
    global paused

    if paused:
        mixer.music.unpause()
        statusbar['text'] = "Music Resumed"
        paused = FALSE
    else:
        try:
            stop_music()
            time.sleep(1)
            selected_song = playlistbox.curselection()
            selected_song = int(selected_song[0])
            play_it = playlist[selected_song]
            mixer.music.load(play_it)
            mixer.music.play()
            statusbar['text'] = "Playing music" + ' - ' + os.path.basename(play_it)
            show_details(play_it)
        except:
            tkinter.messagebox.showerror('File not found', 'Melody could not find the file. Please check again.')


def stop_music():
    mixer.music.stop()
    statusbar['text'] = "Music Stopped"


paused = FALSE


def pause_music():
    global paused
    paused = TRUE
    mixer.music.pause()
    statusbar['text'] = "Music Paused"

    
middleframe = Frame(rightframe,bg="green")
middleframe.grid(row=1,column=0,pady=4)

playPhoto = PhotoImage(file='C:\\Users\\PC\\Downloads\\play.png').subsample(2,2)
playBtn = tkinter.Button(middleframe, image=playPhoto,borderwidth=4,relief="raised",bg="blue", command=play_music)
playBtn.grid(row=0, column=0, padx=10,pady=4)

stopPhoto = PhotoImage(file='C:\\Users\\PC\\Downloads\\pause.png').subsample(2,2)
stopBtn = tkinter.Button(middleframe, image=stopPhoto,cursor='hand2',borderwidth=4,relief="raised",bg="red", command=pause_music)
stopBtn.grid(row=1, column=0, padx=10,pady=4)

rigframe = Frame(classframe,bg="brown")
rigframe.grid(row=0,column=2)
graphbottn=tkinter.Button(rigframe,text="frequence of the song",borderwidth=4,relief="raised",bg="blue",command=graph)
graphbottn.grid(row=1,column=0)

###############################

row2=Frame(classframe,background='brown')
row2.grid(row=1,column=0,pady=50,padx=0,sticky=tkinter.W)
###############################""
boutomfram=Frame(row2,background='brown')
boutomfram.grid(row=0,column=0,pady=50,padx=0,sticky=tkinter.W)
##################################""

machineBtn = tkinter.Button(row2,text="Prediction" ,borderwidth=4,bg="blue",relief="groove",command=typevicule)
machineBtn.grid(row=0,column=0,pady=5,padx=50)


def on_closing():
    stop_music()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()


# In[5]:





# In[ ]:




