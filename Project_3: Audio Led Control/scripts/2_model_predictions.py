import numpy as np
import sounddevice as sd
import tensorflow as tf
from scipy import signal

import tflite_runtime.interpreter as tflite

import time
import sounddevice as sd

def get_project_root():
    import os
    dir_value = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return dir_value

def logger(variable_name , variable_value):
    print(variable_name ," : " , variable_value)

def get_current_microphone_input_device():
    devices = sd.query_devices()
    for i, device in enumerate(devices):
        if device['max_input_channels'] > 0:
            print(f"Device {i}: {device['name']} (Input Channels: {device['max_input_channels']})")
    return devices[sd.default.device]['name']

def change_microphone_input_device(device_name):
    devices = sd.query_devices()
    for i, device in enumerate(devices):
        if device_name in device['name']:
            sd.default.device = i
            print(f"Microphone input device changed to: {device['name']}")
            return
    print(f"Device '{device_name}' not found. Using default device.")

def main():
    root_directory = get_project_root()
    labels = ['off', 'on', 'green', 'red']
    ### Reading Audio from Mic
    duration = 1; fs = 22050
    print("Recording Audio in 1s...")
    time.sleep(1)  
    print("Speak Now ")
    audio_rec = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()
    int_audio = (np.clip(audio_rec, -32768, 32767)) * 32767
    int_audio=int_audio.astype(np.int16)
    int_audio = np.squeeze(int_audio , axis =1)

    ### producing spectrogram
    f, t, spec = signal.stft(int_audio, fs=22050, nperseg=255, noverlap = 124, nfft=256)
    spec=np.abs(spec)
    input_data = np.reshape(spec , (1,1,spec.shape[0],spec.shape[1]) )
    logger("Input Data Shape",input_data.shape)

    ### Model Loading
    #interpreter = tf.lite.Interpreter('data/model/audio_led_model.tflite')
    interpreter = tflite.Interpreter(model_path=root_directory + '/data/model/audio_led_model.tflite')

    input_details   = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    ## model Predicting
    interpreter.allocate_tensors()
    interpreter.set_tensor(input_details[0]['index'] , input_data)
    interpreter.invoke()

    tflite_prediction_result = interpreter.get_tensor(output_details[0]['index'])
    logger("Lite Model Predictions ",labels[np.argmax(tflite_prediction_result)] ) #  labels[np.argmax(tflite_prediction_result)]

if __name__ == '__main__':
    mic_value = get_current_microphone_input_device()
    print(f"Current Microphone Input Device: {mic_value}")
    change_microphone_input_device("USB Audio Device")  # Change to your desired device name
    print("Starting Audio Prediction...")
    time.sleep(1)  # Wait for a second before starting the prediction
    logger("Current Microphone Input Device", get_current_microphone_input_device())
    # main()

    # And Revert microphone Input Device
    change_microphone_input_device(mic_value)
