import pulsectl # For PulseAudio control

import argparse
import sounddevice as sd
from scipy.io.wavfile import write, read
import numpy as np
import time

import sys


def get_pulse_audio_info():
    pulse = pulsectl.Pulse('audio-led-control')
    devices = pulse.source_list()

    for device in devices:
        if device.channel_count <= 0:
            print(f"Skipping device with no channels: {device.name}")
            continue
        # if device.monitor_of:
        #     continue  # Skip monitor sources
        print(f"ID: {device.index}, Name: {device.name}, Channels: {device.channel_count}, "
              f"Sample Rate: {device.sample_spec.rate}")

    pulse.close()

def get_source_names_with_search_term(search_term):
    pulse = pulsectl.Pulse('audio-led-control')
    devices = pulse.source_list()

    matching_devices = []
    for device in devices:
        if device.channel_count <= 0:
            print(f"Skipping device with no channels: {device.name}")
            continue        
        if search_term.lower() in device.name.lower():
            if device.monitor_of_sink_name:
                #print(f"Skipping monitor source: {device.monitor_of_sink_name}")
                continue
            matching_devices.append((device.name, device.description))

    pulse.close()
    return matching_devices


def set_default_sink_with_search_term(search_term) -> bool: 
    pulse = pulsectl.Pulse('audio-led-control')
    sinks = pulse.sink_list()

    result = False

    for sink in sinks:
        if search_term.lower() in sink.name.lower():
            pulse.sink_default_set(sink)
            print(f"Default sink set to: {sink.name}")
            result = True
            break
    else:
        # print(f"Sink '{search_term}' not found.")
        pass

    pulse.close()
    return result


def set_default_source(source_name):
    pulse = pulsectl.Pulse('audio-led-control')
    sources = pulse.source_list()
    
    for source in sources:
        if source.name == source_name:
            pulse.source_default_set(source)
            print(f"Default source set to: {source_name}")
            break
    else:
        print(f"Source '{source_name}' not found.")

    pulse.close()


def record_audio(duration=5, filename='output.wav', sample_rate=44100): 
    print(f"Recording audio for {duration} seconds...")
    recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=2, dtype='int16')
    sd.wait()  # Wait until recording is finished
    write(filename, sample_rate, recording)  # Save as WAV file
    print(f"Audio recorded and saved to {filename}")

def play_audio(filename='output.wav'):
    print(f"Playing audio from {filename}...")
    sample_rate, data = read(filename)
    sd.play(data, samplerate=sample_rate)
    sd.wait()  # Wait until playback is finished
    print("Playback finished.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Audio Control Demo')
    parser.add_argument('--duration', type=int, default=2, help='Duration of recording in seconds')
    parser.add_argument('--filename', type=str, default='test.wav', help='Output WAV filename')
    parser.add_argument('--sample_rate', type=int, default=44100, help='Sample rate for recording')
    parser.add_argument('--search_input', type=str, default=None, help='Search term for input source')
    parser.add_argument('--search_output', type=str, default=None, help='Search term for output sink')
    # parser.add_argument('-h', '--help', action='store_true', help='Show this help message and exit')
    args = parser.parse_args()
    # if args.help:
    #     parser.print_help()
    #     sys.exit(0)
    #get_pulse_audio_info()
    if args.search_input is None:
        search_input_term = "web"
    else:
        search_input_term = args.search_input
    if args.search_output is None:
        search_output_term = "Blaster"
    else:
        search_output_term = args.search_output
    matching_devices = get_source_names_with_search_term(search_input_term)
    if len(matching_devices) == 0:
        if args.search_input is None:
            search_input_term = "Blaster"
            matching_devices = get_source_names_with_search_term(search_input_term)
        if len(matching_devices) == 0:
            print(f"No devices found with search term '{search_input_term}'")
            sys.exit(1)
    
    set_default_source(matching_devices[0][0])
    if not set_default_sink_with_search_term(search_output_term):
        print(f"Failed to set default sink with search term '{search_output_term}'.")
        # Uses current sink              

    print("Recording audio coming...")
    time.sleep(2)  # Wait for 2 seconds before recording
    print(f"Speaking now...")
    record_audio(duration=args.duration, filename=args.filename, sample_rate=args.sample_rate)
    print("Playback of recorded audio...")
    play_audio(filename=args.filename)
