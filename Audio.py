from matplotlib import pyplot as plt
import scipy.signal as sp
import numpy as np
import pyaudio
import time
import serial
from statistics import mean
data = []
port = 'COM4'
baud_rate = 2000000
rate = 44100
record_format = pyaudio.paInt16
channels_amount = 1
buffer = 1024


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
