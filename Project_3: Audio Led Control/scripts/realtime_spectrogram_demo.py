# pip install numpy sounddevice matplotlib

import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Configuration
#SAMPLE_RATE = 44100  # Hz
SAMPLE_RATE = 192000
#SAMPLE_RATE = 384000
block_X=16
BLOCK_SIZE = block_X*1024  # Number of frames per block
WINDOW_SIZE = block_X*1024  # Size of the FFT window
BINS = block_X*512  # Number of frequency bins to display
FPS = 30  # Update window length in seconds
# Logarithmic scale configuration
FREQ_MIN = 20  # Minimum frequency to display (Hz)
FREQ_MAX = SAMPLE_RATE / 2  # Maximum frequency (Nyquist frequency)

USE_LOG_Y_SCALE = False

# Global variables
stream = None
fig, ax = plt.subplots(figsize=(15, 9))
img = None
is_running = True

# Create a logarithmic frequency axis for plotting
log_freq_bins = np.logspace(np.log10(FREQ_MIN), np.log10(FREQ_MAX), BINS)

# We need to map the linear FFT data to these log bins.
# Let's create an interpolation function or similar.
# For simplicity, we'll use linear interpolation between existing bins.
linear_freq_bins = np.linspace(0, SAMPLE_RATE / 2, BINS)
interp_func = lambda x, xp, fp: np.interp(x, xp, fp)

# --- Find the AudioMoth device index ---
def get_audiomoth_device_index():
    """
    Function to find the device index of the AudioMoth.
    """
    global SAMPLE_RATE
    devices = sd.query_devices()
    for i, device in enumerate(devices):
        # The name of the AudioMoth device might vary, but it often
        # contains "USB Audio Device" or something similar.
        if "audiomoth" in device['name'].lower() and device['max_input_channels'] > 0:
            used_sample_rate = int(device['default_samplerate'])
            if used_sample_rate != SAMPLE_RATE:
                print(f"Asked sample rate {SAMPLE_RATE} differs from available {used_sample_rate}")
                SAMPLE_RATE = used_sample_rate
            return i
    return None


def audio_callback(indata, frames, time, status):
    """This function is called for every audio block."""
    global is_running

    if status:
        print(f"Status: {status}")

    if not is_running:
        raise sd.CallbackStop

    # Calculate the FFT of the incoming audio data
    # Use a Hamming window to reduce spectral leakage
    window = np.hamming(len(indata))
    fft_data = np.fft.fft(indata[:, 0] * window, n=WINDOW_SIZE)[:BINS]

    # Calculate the power spectrum and convert to dB
    power_spectrum = np.abs(fft_data)**2
    # Add a small value to avoid log(0)
    db_spectrum = 10 * np.log10(power_spectrum + 1e-10)

    if USE_LOG_Y_SCALE:
        # Re-sample the linear spectrum to fit the logarithmic frequency bins
        log_db_spectrum = interp_func(log_freq_bins, linear_freq_bins, db_spectrum)

    # Update the spectrogram data
    global img
    global FREQ_MIN, FREQ_MAX
    spectrum_up_limit = SAMPLE_RATE / 2
    if img is None:
        # Initialize the spectrogram display
        spectrogram_data = np.zeros((BINS, FPS))
        if not USE_LOG_Y_SCALE:
            img = ax.imshow(spectrogram_data, aspect='auto', origin='lower',
                            extent=[0, FPS, 0, spectrum_up_limit], cmap='viridis')
            ax.set_ylim(0, spectrum_up_limit)  # Limit Y-axis for better visibility
            ax.set_xlabel("Time (s)")
            ax.set_ylabel("Frequency (Hz)")
            ax.set_title("Real-time Spectrogram")
            plt.colorbar(img, label='Power (dB)')
        else:
            img = ax.imshow(spectrogram_data, aspect='auto', origin='lower',
                            extent=[0, FPS, np.log10(FREQ_MIN), np.log10(FREQ_MAX)],
                            cmap='viridis')
            ax.set_ylim(np.log10(FREQ_MIN), np.log10(FREQ_MAX))
            ax.set_yticks(np.log10(np.array([100, 1000, 5000, 10000, 20000, 40000])))
            ax.set_yticklabels(["100", "1k", "5k", "10k", "20k", "40k"])
            ax.set_xlabel("Time (s)")
            ax.set_ylabel("Frequency (Hz)")
            ax.set_title("Real-time Spectrogram (Logarithmic Frequency)")
            plt.colorbar(img, label='Power (dB)')
    else:
        # Shift the existing data and add the new spectrum
        current_data = img.get_array()
        new_data = np.roll(current_data, -1, axis=1)
        new_data[:, -1] = db_spectrum
        img.set_array(new_data)

def animate(frame):
    """Animation function for matplotlib."""
    if img is not None:
        return [img]
    return []

def main():
    global stream, is_running
    print("Starting audio stream and spectrogram...")
    print("Press Ctrl+C to stop.")

    try:
        device_index = get_audiomoth_device_index()
        if device_index is None:
            print("Error: AudioMoth USB microphone not found.")
            print("Please ensure it's connected and has the correct firmware.")
            print("Here are the available input devices:")
            print(sd.query_devices())
            return
        # Open the audio stream
        stream = sd.InputStream(
            samplerate=SAMPLE_RATE,
            blocksize=BLOCK_SIZE,
            callback=audio_callback,
            channels=1,  # Mono audio
            device=device_index
        )
        stream.start()

        # Start the matplotlib animation
        ani = FuncAnimation(fig, animate, interval=1000 / FPS, blit=True)
        plt.show()

    except KeyboardInterrupt:
        print("Stopping audio stream...")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        is_running = False
        if stream and stream.active:
            stream.stop()
        if stream:
            stream.close()
        print("Program terminated.")

if __name__ == "__main__":
    main()
