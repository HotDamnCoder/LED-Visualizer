import numpy as np
import socket
import platform
import sys
import matplotlib.pyplot as plt

CURRENT_OS = platform.system()
CHUNK_SIZE = 1024

ARDUINO_IP_ADDRESS = "192.168.1.139"
ARDUINO_PORT_NUMBER = 8888
CLIENT_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def exit():
    print("Exiting...")
    print("Have a nice day! :)")
    sys.exit()

if CURRENT_OS == 'Linux':
    import alsaaudio

    rate = 44100
    channels = 1
    data_format = alsaaudio.PCM_FORMAT_S16_LE

    MIN_FREQ_BAND = rate / CHUNK_SIZE
    STREAM = alsaaudio.PCM(type=alsaaudio.PCM_CAPTURE,
                           mode=alsaaudio.PCM_NORMAL,
                           rate=rate,
                           channels=channels,
                           format=alsaaudio.PCM_FORMAT_S16_LE,
                           periodsize=CHUNK_SIZE)
elif CURRENT_OS == 'Windows':
    import pyaudio

    PyAudio = pyaudio.PyAudio()
    WASAPI_info = PyAudio.get_host_api_info_by_type(pyaudio.paWASAPI)

    if 'defaultOutputDevice' in WASAPI_info.keys():
        device = PyAudio.get_device_info_by_index(WASAPI_info['defaultOutputDevice'])
    else:
        print("No WASAPI compatible device!")
        # TODO: Add support for stero mix maybe
        exit()

    device_index = device['index']
    rate = int(device['defaultSampleRate'])
    channels = 1
    data_format = pyaudio.paInt16
    
    MIN_FREQ_BAND = rate / CHUNK_SIZE
    STREAM = PyAudio.open(format=data_format,
                          channels=channels,
                          rate=rate,
                          input=True,
                          frames_per_buffer=BUFFER,
                          input_device_index=device_index)


else:
    print("OS not supported!")
    exit()


def getFourierTransform(in_data):
    data = np.frombuffer(in_data, "int16")
    fourier = np.abs(np.fft.rfft(data))
    return fourier


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


def valid_rgb(r, g, b):
    r = max(0, r)
    g = max(0, g)
    b = max(0, b)

    r = min(255, r)
    g = min(255, g)
    b = min(255, b)

    return r, g, b


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


def analyzeData(in_data):
    fourier = getFourierTransform(in_data)
    avg_volume = fourier[0]

    fourier = np.where(fourier > avg_volume, fourier, 0)
    bands = get_bands(fourier)
    band_means = get_bands_mean(bands)

    r, g, b = get_bands_rgb(band_means, avg_volume)
    return r, g, b


def sendColorCode(r, g, b):
    color_code = bytes("R%dG%dB%dE" % (r, g, b), 'utf-8')
    CLIENT_SOCKET.sendto(color_code, (ARDUINO_IP_ADDRESS, ARDUINO_PORT_NUMBER))
    

if __name__ == "__main__":
    print("Starting to read...")
    print("Press to CTRL + C to exit.")
    try:
        while True:
            if CURRENT_OS == 'Linux':
                in_data = STREAM.read()[1]
            elif CURRENT_OS == 'Windows':
                in_data = STREAM.read(CHUNK_SIZE)
            else:
                print("OS not supported!")
                exit()
            r, g, b = analyzeData(in_data)
            sendColorCode(r, g, b)
    except KeyboardInterrupt:
        CLIENT_SOCKET.close()
        print()
        exit()

