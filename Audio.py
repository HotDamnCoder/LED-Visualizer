import numpy as np
import pyaudio
import sys
import serial

# Arduino related variables
PORT = 'COM6'
BAUD_RATE = 2000000

# Initialize pyaudio and get WASAPI info
PyAudio = pyaudio.PyAudio()
WASAPI_info = PyAudio.get_host_api_info_by_type(pyaudio.paWASAPI)
ARDUINO_SERIAL = serial.Serial(PORT, BAUD_RATE, timeout=0.1)

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
    ARDUINO_SERIAL.write(str.encode(str(r) + 'R' + str(g) + 'G' + str(b) + 'B'))

    return in_stream, pyaudio.paContinue


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

STREAM.stop_stream()
STREAM.close()
PyAudio.terminate()
