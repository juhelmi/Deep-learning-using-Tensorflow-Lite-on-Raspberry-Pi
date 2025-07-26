
import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
import time
import os

# Notebook expects 50 samples per category
first_index_for_sample = 0
number_of_repeats = 50
categories = ['on', 'off', 'red', 'green']
#number_of_repeats = 2
#categories = ['green']
#categories = ['nope']


root_directory = os.path.dirname(os.path.abspath(__file__))
root_directory = os.path.dirname(root_directory) + '/'
data_directory = root_directory + 'data_jh/'

if not os.path.exists(data_directory):
    print(f"Creating data directory: {data_directory}")
    os.makedirs(data_directory)

for category in categories:
    print(f"Current category: {category}")
    if not os.path.exists(data_directory + category):
        print(f"Creating directory for category: {category}")
        os.makedirs(data_directory + category)
    time.sleep(1)  # Wait for a second before starting the recording
    for i in range(first_index_for_sample, first_index_for_sample+number_of_repeats):
        #category = 'green'
        file_name = category+"_" + f"{i:02d}"  # Format the number with leading zeros
        duration = 1  # seconds
        fs = 22050
        print(" Speak now -> " , category)
        audio_rec = sd.rec(int(duration * fs), samplerate=fs, channels=1)
        sd.wait()
        int_audio = (np.clip(audio_rec, -32768, 32767)) * 32767
        write(data_directory +category + "/" + file_name + ".wav", fs, int_audio.astype(np.int16))

        print("Recorded -> ", i)
        time.sleep(0.5)