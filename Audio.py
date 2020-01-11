import matplotlib.pyplot as plt
import numpy as np
import pyaudio
import time
import serial

saved_r = 0
saved_g = 0
saved_b = 0
saved_w = 0

port = 'COM6'
baud_rate = 2000000
rate = 44100
record_format = pyaudio.paInt16
channels_amount = 1
buffer = 1024


def map_amplitude_w(w, amplitude):
    loudness_multiplier = 255 / 16384
    amplitude = int(amplitude * loudness_multiplier)
    if amplitude >= 127:
        amplitude = (amplitude - 127) * 1
        w += amplitude

    else:
        amplitude = abs(amplitude - 127) * 1
        w -= amplitude
    return w


def map_amplitude(r, g, b, amplitude):
    loudness_multiplier = 255 / 16384
    amplitude = int(amplitude * loudness_multiplier)
    if amplitude == 0:
        r = 0
        g = 0
        b = 0
    if amplitude >= 127:
        amplitude = (amplitude - 127) * 1
        r += amplitude
        g += amplitude
        b += amplitude
    else:
        amplitude = abs(amplitude - 127) * 1
        r -= amplitude
        g -= amplitude
        b -= amplitude
    return r, g, b


def map_pitch(r, g, b, frequency):
    frequency_multiplier = 255 / 3676
    if 0 <= frequency <= 7350:
        r = 255
        if frequency > 3676:
            frequency = int((frequency-3676) * frequency_multiplier)
            g = frequency
        else:
            frequency = int(frequency * frequency_multiplier)
            b = frequency
    elif 7351 <= frequency <= 14700:
        g = 255
        if frequency > 11026:
            frequency = int((frequency - (3676 + 7350)) * frequency_multiplier)
            g = frequency
        else:
            frequency = int((frequency - 7350) * frequency_multiplier)
            b = frequency
    else:
        b = 255
        if frequency > 18376:
            frequency = int((frequency - (3676 + 7350*2)) * frequency_multiplier)
            g = frequency
        else:
            frequency = int((frequency - 7350 * 2) * frequency_multiplier)
            b = frequency
    return r, g, b


def check_if_changed(r, g, b, amount):
    if abs(r-saved_r) > amount:
        r = saved_r
    if abs(g - saved_g) > amount:
        g = saved_g
    if abs(r - saved_b) > amount:
        b = saved_b
    return r, g, b


def normalize(r, g, b):
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


def map_to_rgb(frequency, amplitude, change_necessary):
    r = g = b = 0
    r, g, b = map_pitch(r, g, b, frequency)
    r, g, b = map_amplitude(r, g, b, amplitude)
    r, g, b = normalize(r, g, b)
    print(r, g, b)
    return r, g, b


def search_for_averages(fourier, avg_frequency_amplitude):
    avg_frequencies = np.where(np.abs(fourier - avg_frequency_amplitude) < 100)[0]
    if avg_frequencies.size == 0:
        avg_frequencies = np.where(np.abs(fourier - avg_frequency_amplitude) < 500)[0]
        if avg_frequencies.size == 0:
            count = 1
            while avg_frequencies.size == 0:
                avg_frequencies = np.where(np.abs(fourier - avg_frequency_amplitude) < 1000 * count)[0]
                count += 1
    return avg_frequencies


def callback(in_data, frame_count, time_info, status):
    change_necessary = 0
    data_numpy_array = np.frombuffer(in_data, "int16")
    fourier = np.abs(np.fft.rfft(data_numpy_array))
    """ testing stuff
    loudest_frequency = np.where(fourier == fourier.max())[0] * (rate / len(data_numpy_array))
    max_loudness = np.abs(data_numpy_array).max()
    """
    avg_amplitude = np.average(np.abs(data_numpy_array))
    avg_frequency_amplitude = np.average(fourier)
    avg_frequencies = search_for_averages(fourier, avg_frequency_amplitude)
    avg_frequency = np.average(avg_frequencies) * (rate / len(data_numpy_array))
    print(avg_frequency, avg_amplitude)
    r, g, b = map_to_rgb(int(avg_frequency), int(avg_amplitude), change_necessary)
    output = str(r) + 'R' + str(g) + 'G' + str(b) + 'B'
    #arduino_serial.write(output.encode())
    return in_data, pyaudio.paContinue


#arduino_serial = serial.Serial(port, baud_rate, timeout=0)
#time.sleep(2)
p = pyaudio.PyAudio()
stream = p.open(format=record_format,
                channels=channels_amount,
                rate=rate,
                input=True,
                frames_per_buffer=buffer,
                stream_callback=callback,
                input_device_index=2)

print("recording")
stream.start_stream()
while stream.is_active():
    time.sleep(0.1)
stream.stop_stream()
stream.close()
p.terminate()
