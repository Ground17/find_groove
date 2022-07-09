import subprocess
import datetime
from multiprocessing import Process
import time
import webbrowser

from flask import Flask, render_template, request, jsonify
import compare
import spectrogram
import tensorflow as tf
import os
import numpy as np
import pickle
from tkinter import LEFT, W, Button, Entry, Label, IntVar, Radiobutton
import tkinter.ttk
from tkinter.filedialog import askdirectory
    
# app = Flask(__name__)

# @app.route('/')
# def main():
#     dummy_times = [datetime.datetime(2022, 6, 1, 23, 59, 59)]
#     return render_template('index.html', times=dummy_times)

# @app.route('/search', methods=['POST'])
# def search():
#     return jsonify("")

window=tkinter.Tk()
window.title("Find Groove")

is_model = False
port = 8080

def draw_window_1():
    description1 = Label(window, text="1. Choose a folder(directory) that contains *.wav file(s).", justify=LEFT, anchor='w')
    directory_btn = Button(window, text='Select', command=directory)
    description1.grid(row=0, column=0, columnspan=2, sticky = W)
    directory_btn.grid(row=0, column=2)

def directory():
    global filepath
    filepath = askdirectory(title="Dialog box", initialdir=os.getcwd())
    label_path = Label(window, text=filepath)
    label_path.grid(row=1, column=0, columnspan=3)

    # show for making fingerprint
    if filepath:
        description2 = Label(window, text="2. Make a fingerprint file.\nIf 'fingerprints' is already in the path, skip this process.", justify=LEFT, anchor='w')
        fingerprint_btn = Button(window, text='Make', command=make_fingerprint)
        skip_btn = Button(window, text='Skip', command=load_tuple)
        description2.grid(row=2, column=0, sticky = W)
        skip_btn.grid(row=2, column=1)
        fingerprint_btn.grid(row=2, column=2)

def make_fingerprint():
    global filepath, finger_dict
    music_list = os.listdir(filepath)
    music_list = [item for item in music_list if os.path.isfile(os.path.join(filepath, item)) and item.split('.')[-1] == 'wav'] # pick *.wav files

    fan_value = 15 # 특정 인덱스 기준 몇번째까지 범위를 가질것인가
    finger_dict = {}
    progressbar = tkinter.ttk.Progressbar(window, length=len(music_list), mode="determinate")
    progressbar.grid(row=3, column=0, columnspan=2)
    progress_label = Label()
    progress_label.grid(row=3, column=2)
    progressbar.start(10)

    for k, name in enumerate(music_list):
        print(name)
        peaks = spectrogram.spectrogram(filepath + "/" + name, weight = 0.6)
        for i in range(len(peaks)):
            for j in range(1, fan_value):
                if (i + j) < len(peaks): # 인덱스가 범위 내에 있다면
                    freq1 = peaks[i][0] # 주파수1 인덱스
                    freq2 = peaks[i + j][0] # 주파수2 인덱스
                    t1 = peaks[i][1] # 시간1 인덱스
                    t2 = peaks[i + j][1] # 시간2 인덱스
                    t_delta = t2 - t1

                    if t_delta <= 1024 * 20:
                        if (freq1, freq2, t_delta) not in finger_dict:
                            finger_dict[(freq1, freq2, t_delta)] = set()

                        finger_dict[(freq1, freq2, t_delta)].add((name, t1)) # key: (freq1, freq2, t_delta), value: (filename, t1)

        # progress_label.config(text=str(k + 1) + "/" + str(len(music_list)))

    # print(finger_dict)

    with open(filepath + '/fingerprints', 'wb') as f:
        pickle.dump(finger_dict, f)

    draw_window_3()

def load_tuple(): # load fingerprint 튜플 불러오기
    global filepath, finger_dict
    with open(filepath + '/fingerprints', 'rb') as f:
        finger_dict = pickle.load(f)
    
    draw_window_3()

def draw_window_3():
    description3 = Label(window, text="3. Verify that the tensorflow model is in the path.\nSee 'https://github.com/Ground17/find_groove' for a detailed description of the model.", justify=LEFT, anchor='w')
    directory_btn = Button(window, text='Check', command=check_model)
    description3.grid(row=4, column=0, columnspan=2, sticky = W)
    directory_btn.grid(row=4, column=2)

def check_model(): # tensorflow model을 사용할 것인지 체크
    global filepath, is_model, model

    try:
        if os.path.exists(filepath + '/cnn_vote_best_total.h5'):
            model = tf.keras.models.load_model(filepath + '/cnn_vote_best_total.h5')
            is_model = True
        else:
            is_model = False
    except:
        is_model = False

    label_model = Label(window, text="We can use tensorflow model!" if is_model else "We can't use tensorflow model.")
    label_model.grid(row=5, column=0, columnspan=3)

    draw_window_4()

def draw_window_4():
    global radio_var, port, port_entry
    description4 = Label(window, text="4. Set mode and turn on the server.\n'local' mode can only run on devices running the server, and 'global' mode can also run on other devices (such as smartphones) in the same network.\nIn the case of 'global' mode, you may need to set up a separate firewall, etc.", justify=LEFT, anchor='w')
    directory_btn = Button(window, text='Turn on', command=run_process)
    description4.grid(row=6, column=0, columnspan=3, sticky = W)

    frame = tkinter.Frame(window)
    scope_frame = tkinter.LabelFrame(frame, text="scope")
    radio_var = IntVar()
    local_radio = Radiobutton(scope_frame, text="local", value=0, variable=radio_var)
    local_radio.select()
    global_radio = Radiobutton(scope_frame, text="global", value=1, variable=radio_var)

    local_radio.grid(row=0, column=0)
    global_radio.grid(row=0, column=1)

    port_frame = tkinter.LabelFrame(frame, text="port")
    port_entry = Entry(port_frame)
    port_entry.insert(0, str(port))
    port_entry.pack()

    scope_frame.grid(row=0, column=0)
    port_frame.grid(row=0, column=1)
    frame.grid(row=7, column=0, columnspan=2)
    directory_btn.grid(row=7, column=2)

def run_process():
    global test_lists, radio_var, port_entry, port
    try:
        port = port_entry.getint()
        if port > 65535 or port < 0:
            port = 8080
    except:
        port = 8080

    # draw_window_1()
    # window.mainloop()

# def stop_local():
#     func = request.environ.get('werkzeug.server.shutdown')
#     if func is None:
#         raise RuntimeError('Not running with the Werkzeug Server')
#     func()