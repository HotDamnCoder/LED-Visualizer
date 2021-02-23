import numpy as np
import sounddevice as sd
import socket
import pygame

pygame.init()
screen = pygame.display.set_mode((400, 300))

UDP_IP_ADDRESS = "192.168.1.139"
UDP_PORT_NUMBER = 8888


RATE = 44100
CHANNELS = 2
FORMAT = np.int16
BUFFER = 1024
MIN_FREQ_BAND = RATE / BUFFER
FOURIER_LEN = int(BUFFER / 2)
clientsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def get_fourier_from_stream(stream):
    data = np.frombuffer(stream, "int16")
    fourier = np.abs(np.fft.rfft(data[::2]))
    fourier[0] = 0
    avg_volume = 10 * np.log10(np.mean(fourier))
    return fourier, avg_volume


def get_bands(fourier):

    bass_band_limit = 400
    midrange_limit = 1000
    upper_limit = 4000

    bass_band = fourier[1:int(bass_band_limit / MIN_FREQ_BAND)]
    midrange_band = fourier[int(bass_band_limit / MIN_FREQ_BAND):int(midrange_limit / MIN_FREQ_BAND)]
    upper_band = fourier[int(midrange_limit / MIN_FREQ_BAND):int(upper_limit / MIN_FREQ_BAND):]

    return bass_band, midrange_band, upper_band


def get_bands_mean(bands):
    return [np.mean(band) for band in bands]


def get_bands_mean_db(bands_mean):
    return [10 * (np.log10(band_mean) if band_mean != 0 else 0) for band_mean in bands_mean]


def get_bands_rgb(bands_means, avg_volume):
    max_amplitude = 60
    min_amplitude = 15
    r, g, b = 0, 0, 0
    if avg_volume > min_amplitude:
        r, b, g = get_bands_mean_db(bands_means)

        r = r - min_amplitude
        g = g - min_amplitude
        b = b - min_amplitude

        r = int(255 * (r / max_amplitude))
        b = int(255 * (b / max_amplitude))
        g = int(255 * (g / max_amplitude))

        r, g, b = valid_rgb(r, g, b)

    return r, g, b


def get_rgb(data):
    # red part / bass part
    bass_band = data[1: round(250 / MIN_FREQ_BAND)]
    peak_bass = np.argmax(bass_band) + 1
    r = int(peak_bass * 255 / len(bass_band))

    medium_band = data[round(250 / MIN_FREQ_BAND): round(2000 / MIN_FREQ_BAND)]
    peak_medium = np.argmax(medium_band) + 1
    g = int(peak_medium * 255 / len(medium_band))

    high_band = data[round(2000 / MIN_FREQ_BAND): round(6000 / MIN_FREQ_BAND)]
    peak_high = np.argmax(high_band) + 1
    b = int(peak_high * 255 / len(high_band))
    return r, g, b


def valid_rgb(r, g, b):
    r = max(0, r)
    g = max(0, g)
    b = max(0, b)

    r = min(255, r)
    g = min(255, g)
    b = min(255, b)

    return r, g, b


def callback(in_stream, frame_count, time_info, status):
    fourier, avg_volume = get_fourier_from_stream(in_stream)
    fourier = np.where(fourier > avg_volume, fourier, 0)
    # r, g, b = get_rgb(fourier)
    bands = get_bands(fourier)
    band_means = get_bands_mean(bands)
    r, g, b = get_bands_rgb(band_means, avg_volume)
    message = "R" + str(r) + "G" + str(g) + "B" + str(b)
    clientsocket.sendto(bytes(message, 'utf-8'), (UDP_IP_ADDRESS, UDP_PORT_NUMBER))
    screen.fill([r, g,b])
    pygame.display.flip()


STREAM = sd.InputStream(
        samplerate=RATE,
        blocksize=BUFFER,
        channels=CHANNELS,
        dtype=FORMAT,
        callback=callback)

with STREAM:
    while(True):
        for event in pygame.event.get():
            continue

STREAM.stop()
