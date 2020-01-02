import pyaudio as py
import matplotlib.pyplot as plt
import numpy as np
import pyaudio
import time


def map_to_rgb(frequency, loudness):
    loudness_multiplier = 255 / 16384
    frequency_multiplier = 255 / 3676
    loudness = int(loudness * loudness_multiplier)
    r = 0
    g = 0
    b = 0
    if 0 <= frequency <= 7350:
        r = 255
        if frequency > 3676:
            g = int((frequency - 3676) * frequency_multiplier)
        else:
            b = int((3676 - frequency) * frequency_multiplier)
    elif 7351 <= frequency <= 14700:
        g = 255
        if frequency > 11026:
            g = int((frequency - 11026) * frequency_multiplier)
        else:
            b = int((11026 - frequency) * frequency_multiplier)
    else:
        b = 255
        if frequency > 18376:
            g = int((frequency - 18376) * frequency_multiplier)
        else:
            b = int((18376 - frequency) * frequency_multiplier)
    if loudness >= 127:
        r += loudness
        g += loudness
        b += loudness
    else:
        r -= loudness
        g -= loudness
        b -= loudness
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
    elif r > 255:
        b = 255
    return r, g, b


def callback(in_data, frame_count, time_info, status):
    data_numpy_array = np.frombuffer(in_data, "int16")
    fourier = np.abs(np.fft.rfft(data_numpy_array))
    """ testing stuff
    loudest_frequency = np.where(fourier == fourier.max())[0] * (rate / len(data_numpy_array))
    max_loudness = np.abs(data_numpy_array).max()
    """
    avg_loudness = np.average(np.abs(data_numpy_array))
    avg_frequency_loudness = np.average(fourier)
    what = np.where(np.abs(fourier - avg_frequency_loudness) < 2000)
    avg_frequency = np.average(what) * (rate / len(data_numpy_array))
    """ testing stuff
    data.extend(data_numpy_array)
    avg_loudnesses.append(avg_loudness)
    avg_frequencies.append(avg_frequency)
    max_loudnesses.append(max_loudness)
    loudest_frequencies.append(loudest_frequency)
    """

    print(map_to_rgb(int(avg_frequency), int(avg_loudness)))
    return in_data, pyaudio.paContinue


p = py.PyAudio()
rate = 44100
record_format = pyaudio.paInt16
channels_amount = 1
buffer = 512
seconds = 10
data = []
max_loudnesses = []
loudest_frequencies = []

stream = p.open(format=record_format,
                channels=channels_amount,
                rate=rate,
                input=True,
                frames_per_buffer=buffer,
                stream_callback=callback,
                input_device_index=2)
"""testing stuff
avg_loudnesses = []
avg_frequencies = []
"""
print("* recording")
stream.start_stream()
while stream.is_active():
    time.sleep(0.1)
print("* done recording")
stream.stop_stream()
stream.close()
p.terminate()
""" testing stuff
avg_loudnesses = np.array(avg_loudnesses)
avg_frequencies = np.array(avg_frequencies)
max_loudnesses = np.array(max_loudnesses)
loudest_frequencies = np.array(loudest_frequencies)
time = np.arange(0, float(max_loudnesses.shape[0]), 1) / 44100 * 1000
plt.figure(1)
plt.subplot(211)
plt.plot(time, max_loudnesses)
plt.subplot(212)
plt.plot(time, loudest_frequencies)
plt.show()
plt.figure(1)
plt.subplot(211)
plt.plot(time, avg_loudnesses)
plt.subplot(212)
plt.plot(time, avg_frequencies)
plt.show()
"""

