<<<<<<< HEAD
=======
from matplotlib import pyplot as plt
import scipy.signal as sp
>>>>>>> c5873d914563cc7aaa3fc5e96c8d4bf8b9caa3f5
import numpy as np
import pyaudio
import pygame
import sys
import serial
<<<<<<< HEAD
import time


# Arduino related variables
PORT = 'COM11'
BAUD_RATE = 2000000
arduino = serial.Serial(PORT, BAUD_RATE, timeout=.1)
=======
from statistics import mean
data = []
port = 'COM4'
baud_rate = 2000000
rate = 44100
record_format = pyaudio.paInt16
channels_amount = 1
buffer = 1024
>>>>>>> c5873d914563cc7aaa3fc5e96c8d4bf8b9caa3f5

# Initialize pyaudio and get WASAPI info
PyAudio = pyaudio.PyAudio()
WASAPI_info = PyAudio.get_host_api_info_by_type(pyaudio.paWASAPI)

<<<<<<< HEAD
# Get default WASAPI output if available else exit
try:
    default_WASAPI_output = PyAudio.get_device_info_by_index(WASAPI_info['defaultOutputDevice'])
except KeyError:
    print("No WASAPI default output. Exiting...")
    sys.exit()

# Get appropriate info about the default WASAPI output device
DEVICE_INDEX = default_WASAPI_output['index']
RATE = int(default_WASAPI_output['defaultSampleRate'])
CHANNELS = default_WASAPI_output['maxOutputChannels']
FORMAT = pyaudio.paInt16
BUFFER = 1024
MIN_FREQ_BAND = RATE / BUFFER
FOURIER_LEN = int(BUFFER / 2)
#screen = pygame.display.set_mode((480, 480))


def get_fourier_from_stream(stream):
    data = np.frombuffer(stream, "int16")
    fourier = np.abs(np.fft.rfft(data[::2]))
    fourier[0] = 0
    avg_volume = 10 * np.log10(np.mean(fourier))
    return fourier, avg_volume


def get_bands(fourier):

    bass_band_limit = 200
    midrange_limit = 1500
    upper_limit = 8000

    bass_band = fourier[1:int(bass_band_limit / MIN_FREQ_BAND)]
    midrange_band = fourier[int(bass_band_limit / MIN_FREQ_BAND):int(midrange_limit / MIN_FREQ_BAND)]
    upper_band = fourier[int(midrange_limit / MIN_FREQ_BAND):int(upper_limit / MIN_FREQ_BAND):]

    return bass_band, midrange_band, upper_band


def get_bands_mean(bands):
    return [np.mean(band) for band in bands]


def get_bands_mean_db(bands_mean):
    return [10 * (np.log10(band_mean) if band_mean != 0 else 0) for band_mean in bands_mean]

=======
def map_amplitude_to_white(amplitude):
    amplitude *= (255 / 32768)
    w = int(round(amplitude))
    return w


def map_instruments(instrument_frequencies_amplitude):
    instrument_frequencies_amplitude *= (255 / 3275.22)
    b = int(round(instrument_frequencies_amplitude))
    return b


def map_vocals(vocal_frequencies_amplitude):

    vocal_frequencies_amplitude *= (255/1830.27)
    g = int(round(vocal_frequencies_amplitude))
    return g


def map_bass(bass_frequencies_amplitude):
    bass_frequencies_amplitude *= (255 / 288.99)
    r = int(round(bass_frequencies_amplitude))
    return r


def map_amplitude_over_pitch(r, g, b, amplitude):
    amplitude *= (255 / 32768)
    amplitude_var = amplitude
    amplitude_var = abs(amplitude_var - 127)
    amplitude_var *= (255/127)
    if amplitude >= 127:
        if r == 255:
            g += amplitude_var  # Dived by 2?
            b += amplitude_var
        elif g == 255:
            r += amplitude_var
            b += amplitude_var
        else:
            r += amplitude_var
            g += amplitude_var
    else:
        if r == 255:
            r -= amplitude_var
            g -= amplitude_var / 2
            b -= amplitude_var / 2
        elif g == 255:
            g -= amplitude_var
            r -= amplitude_var / 2
            b -= amplitude_var / 2
        else:
            b -= amplitude_var
            r -= amplitude_var / 2
            g -= amplitude_var / 2
    return round(r), round(g), round(b)
>>>>>>> c5873d914563cc7aaa3fc5e96c8d4bf8b9caa3f5

def get_bands_rgb(bands_means, avg_volume):
    r, g, b = 0, 0, 0
    max_amplitude = 110
    min_amplitude = 13
    if avg_volume > min_amplitude:
        r, g, b = get_bands_mean_db(bands_means)

<<<<<<< HEAD
        r = r - min_amplitude
        g = g - min_amplitude
        b = b - min_amplitude

        r = int(255 * (r / max_amplitude))
        g = int(255 * (g / max_amplitude))
        b = int(255 * (b / max_amplitude))
        #r, g, b = fck_this_shit_up(r,g,b)
        r, g, b = valid_rgb(r, g, b)


    return r, g, b

def fck_this_shit_up(r,g,b):
    boost = 0
    slow = 25
    if r > g and r > b:
        r += boost
        g -= slow
        b -= slow
    elif g > b and g > r:
        g += boost
        r -= slow
        b -= slow
    else:
        b += boost
        r -= slow
        g -= slow
    return r, g, b


def get_rgb(data):
    # red part / bass part
    bass_band = data[1: round(250 / MIN_FREQ_BAND)]
    peak_bass = np.argmax(bass_band) + 1
    r = int(peak_bass * 255 / len(bass_band))
=======
def map_pitch_to_r_g_b(frequency):
    frequency_multiplier = 255 / 3676
    r = g = b = 0
    if 0 <= frequency <= 7350:
        r = 255
        if frequency > 3676:
            frequency = (frequency - 3676) * frequency_multiplier
            g = frequency
        elif frequency != 3676:
            frequency = frequency * frequency_multiplier
            b = frequency
    elif 7351 <= frequency <= 14700:
        g = 255
        if frequency > 11026:
            frequency = (frequency - (3676 + 7350)) * frequency_multiplier
            b = frequency
        elif frequency != 11026:
            frequency = (frequency - 7350) * frequency_multiplier
            r = frequency
    else:
        b = 255
        if frequency > 18376:
            frequency = (frequency - (3676 + 7350 * 2)) * frequency_multiplier
            r = frequency
        elif frequency != 18376:
            frequency = (frequency - 7350 * 2) * frequency_multiplier
            g = frequency

    return round(r), round(g), round(b)
>>>>>>> c5873d914563cc7aaa3fc5e96c8d4bf8b9caa3f5

    medium_band = data[round(250 / MIN_FREQ_BAND): round(2000 / MIN_FREQ_BAND)]
    peak_medium = np.argmax(medium_band) + 1
    g = int(peak_medium * 255 / len(medium_band))

    high_band = data[round(2000 / MIN_FREQ_BAND): round(6000 / MIN_FREQ_BAND)]
    peak_high = np.argmax(high_band) + 1
    b = int(peak_high * 255 / len(high_band))

<<<<<<< HEAD
    return r, g, b


def valid_rgb(r, g, b):
    r = max(0, r)
    g = max(0, g)
    b = max(0, b)

    r = min(255, r)
    g = min(255, g)
    b = min(255, b)

    return int(r), int(g), int(b)


def callback(in_stream, frame_count, time_info, status):
    fourier, avg_volume = get_fourier_from_stream(in_stream)
    fourier = np.where(fourier > avg_volume, fourier, 0)
    # r, g, b = get_rgb(fourier)
    bands = get_bands(fourier)
    band_means = get_bands_mean(bands)
    r, g, b = get_bands_rgb(band_means, avg_volume)
    arduino.write(str.encode(str(r) + "R" + str(g) + "G" + str(b) + "B"))
    print('\r', r, g, b, end="")
    """screen.fill((r, g, b))
    pygame.display.flip()"""

    return in_stream, pyaudio.paContinue

time.sleep(1)
STREAM = PyAudio.open(format=FORMAT,
                      channels=CHANNELS,
                      rate=RATE,
                      input=True,
                      frames_per_buffer=BUFFER,
                      stream_callback=callback,
                      input_device_index=DEVICE_INDEX,
                      as_loopback=True)

STREAM.start_stream()

print("Starting recording...")

while STREAM.is_active():
    pass
    #for event in pygame.event.get():
        #continue

STREAM.stop_stream()
STREAM.close()
PyAudio.terminate()
=======
def normalize_r_g_b(r, g, b):
    if r < 0:
        r = 0
    elif r > 255:
        r = 255
    if g < 0:
        g = 0
    elif g > 255:
        g = 255
    if b < 0:
        b = 0
    elif b > 255:
        b = 255
    return r, g, b


def map_to_rgb(frequencies, amplitude):
    # r, g, b = map_pitch_to_r_g_b(frequencies[101:])
    frequencies = np.where(frequencies == 0, 0.0001, frequencies)
    frequencies = 10*np.log10(frequencies)
    w = map_amplitude_to_white(amplitude)
    # print(np.argmax(frequencies[0:4])*43, (np.argmax(frequencies[4:25]) +4)*43,(np.argmax(frequencies[25:59])+25)*43)
    r = map_bass(np.sum(frequencies[0:4]))
    g = map_vocals(np.sum(frequencies[4:25]))
    b = map_instruments(np.sum(frequencies[25:59]))
    print(r,g,b,w)
  
    r, g, b = normalize_r_g_b(r, g, b)
    return r, g, b, w


def callback(in_data, frame_count, time_info, status):
    # Data processing
    data_numpy_array = np.frombuffer(in_data, "int16") * np.hamming(buffer)
    fourier = np.abs(np.fft.fft(data_numpy_array))[:int(buffer/2)]
    frequency_resolution = rate / len(data_numpy_array)
    amplitude = np.abs(data_numpy_array)
    fourier[0] = 0
    plt.plot(np.arange(0,len(fourier)) * (44100/1024), 10 * np.log10(fourier))
    plt.show()
    # Max amplitude and loudest_frequency
    max_amplitude = amplitude.max()
    # Average amplitude and frequency
    avg_amplitude = np.average(amplitude)
    # Mapping to RGBW and outputting

    r, g, b, w = map_to_rgb(fourier, int(max_amplitude))
    #output = str(r) + 'R' + str(g) + 'G' + str(b) + 'B' + str(w) + 'W'
    #print(output)

    return None, pyaudio.paContinue

p = pyaudio.PyAudio()
stream = p.open(format=record_format,
                channels=channels_amount,
                rate=rate,
                input=True,
                frames_per_buffer=buffer,
                stream_callback=callback,
                input_device_index=2)

#arduino_serial = serial.Serial(port, baud_rate, timeout=0.1)
time.sleep(2)
print("recording")
stream.start_stream()
while stream.is_active():
    time.sleep(5)

stream.stop_stream()
stream.close()
p.terminate()
>>>>>>> c5873d914563cc7aaa3fc5e96c8d4bf8b9caa3f5
