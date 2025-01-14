import cv2
import os
from keras.models import load_model
import numpy as np
from pygame import mixer
import time
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

mixer.init()
sound = mixer.Sound('alarm.wav')

face = cv2.CascadeClassifier('haar cascade files\\haarcascade_frontalface_alt.xml')
leye = cv2.CascadeClassifier('haar cascade files\\haarcascade_lefteye_2splits.xml')
reye = cv2.CascadeClassifier('haar cascade files\\haarcascade_righteye_2splits.xml')

lbl = ['Close', 'Open']
model = load_model('models/cnncat2.h5')
path = os.getcwd()
cap = cv2.VideoCapture(0)
font = cv2.FONT_HERSHEY_COMPLEX_SMALL
count = 0
score = 0
thicc = 2
rpred = [99]
lpred = [99]

class DrowsinessDetectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Driver Drowsiness Detection")
        self.root.geometry("800x600")
        
        self.label = tk.Label(root)
        self.label.pack()

        self.start_button = tk.Button(root, text="Start Detection", command=self.start_detection)
        self.start_button.pack()

        self.stop_button = tk.Button(root, text="Stop Detection", command=self.stop_detection)
        self.stop_button.pack()

        self.detection_running = False

    def start_detection(self):
        self.detection_running = True
        self.detect_drowsiness()

    def stop_detection(self):
        self.detection_running = False

    def detect_drowsiness(self):
        global count, score, thicc, rpred, lpred
        if self.detection_running:
            ret, frame = cap.read()
            if not ret:
                messagebox.showerror("Error", "Failed to capture video")
                return

            height, width = frame.shape[:2]
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face.detectMultiScale(gray, minNeighbors=5, scaleFactor=1.1, minSize=(25, 25))
            left_eye = leye.detectMultiScale(gray)
            right_eye = reye.detectMultiScale(gray)

            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 1)

            for (x, y, w, h) in right_eye:
                r_eye = frame[y:y + h, x:x + w]
                r_eye = cv2.cvtColor(r_eye, cv2.COLOR_BGR2GRAY)
                r_eye = cv2.resize(r_eye, (24, 24))
                r_eye = r_eye / 255
                r_eye = r_eye.reshape(24, 24, -1)
                r_eye = np.expand_dims(r_eye, axis=0)
                rpred = np.argmax(model.predict(r_eye), axis=-1)
                if rpred[0] == 1:
                    lbl = 'Open'
                if rpred[0] == 0:
                    lbl = 'Closed'
                break

            for (x, y, w, h) in left_eye:
                l_eye = frame[y:y + h, x:x + w]
                l_eye = cv2.cvtColor(l_eye, cv2.COLOR_BGR2GRAY)
                l_eye = cv2.resize(l_eye, (24, 24))
                l_eye = l_eye / 255
                l_eye = l_eye.reshape(24, 24, -1)
                l_eye = np.expand_dims(l_eye, axis=0)
                lpred = np.argmax(model.predict(l_eye), axis=-1)
                if lpred[0] == 1:
                    lbl = 'Open'
                if lpred[0] == 0:
                    lbl = 'Closed'
                break

            if rpred[0] == 0 and lpred[0] == 0:
                score += 1
                cv2.putText(frame, "Closed", (10, height - 20), font, 1, (0, 0, 255), 1, cv2.LINE_AA)
            else:
                score -= 1
                cv2.putText(frame, "Open", (10, height - 20), font, 1, (0, 255, 0), 1, cv2.LINE_AA)

            if score < 0:
                score = 0
            cv2.putText(frame, 'Score:' + str(score), (100, height - 20), font, 1, (255, 255, 255), 1, cv2.LINE_AA)
            if score > 15:
                cv2.imwrite(os.path.join(path, 'image.jpg'), frame)
                try:
                    sound.play()
                except:
                    pass
                thicc = thicc + 2
                if thicc > 16:
                    thicc = thicc - 2
                cv2.rectangle(frame, (0, 0), (width, height), (0, 0, 255), thicc)

            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            imgtk = ImageTk.PhotoImage(image=img)
            self.label.imgtk = imgtk
            self.label.configure(image=imgtk)
            self.label.after(10, self.detect_drowsiness)

root = tk.Tk()
app = DrowsinessDetectionApp(root)
root.mainloop()
