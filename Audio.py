# ! https://www.nti-audio.com/en/support/know-how/fast-fourier-transform-fft good resource about fft
import numpy as np
import socket
import platform
import sys


MAX_AMP = 10 ** (110 / 10)

ARDUINO_IP_ADDRESS = "esp8266.local"
ARDUINO_PORT_NUMBER = 8888
CLIENT_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
CURRENT_OS = platform.system()

CHUNK_SIZE = 1024

if CURRENT_OS == 'Linux':
    import alsaaudio

    rate = 44100
    channels = 1
    data_format = alsaaudio.PCM_FORMAT_S16_LE

    FREQ_RESOLUTION = rate / CHUNK_SIZE
    STREAM = alsaaudio.PCM(type=alsaaudio.PCM_CAPTURE,
                           mode=alsaaudio.PCM_NORMAL,
                           rate=rate,
                           channels=channels,
                           format=alsaaudio.PCM_FORMAT_S32_LE,
                           periodsize=CHUNK_SIZE)
elif CURRENT_OS == 'Windows':
    import pyaudio

    PyAudio = pyaudio.PyAudio()
    WASAPI_info = PyAudio.get_host_api_info_by_type(pyaudio.paWASAPI)

    if 'defaultOutputDevice' in WASAPI_info.keys():
        device = PyAudio.get_device_info_by_index(
            WASAPI_info['defaultOutputDevice'])
    else:
        print("No WASAPI compatible device!")
        # TODO: Add support for stero mix maybe
        exit()

    device_index = device['index']
    rate = int(device['defaultSampleRate'])
    channels = 1
    data_format = pyaudio.paInt32

    FREQ_RESOLUTION = rate / CHUNK_SIZE
    STREAM = PyAudio.open(format=data_format,
                          channels=channels,
                          rate=rate,
                          input=True,
                          frames_per_buffer=CHUNK_SIZE,
                          input_device_index=device_index)
else:
    print("OS not supported!")
    exit()

BASE_BAND_UPPER_LIMIT = round(600 / FREQ_RESOLUTION)
MIDRANGE_BAND_UPPER_LIMIT = round(2400 / FREQ_RESOLUTION)
UPPERRANGE_BAND_UPPER_LIMIT = round(9600 / FREQ_RESOLUTION)


def exit():
    print("Exiting...")
    print("Have a nice day! :)")
    sys.exit()


def readInputStream():
    if CURRENT_OS == 'Linux':
        in_stream = STREAM.read()[1]
    elif CURRENT_OS == 'Windows':
        in_stream = STREAM.read(CHUNK_SIZE)
    return in_stream


def closeInputStream():
    if CURRENT_OS == 'Linux':
        pass
    elif CURRENT_OS == 'Windows':
        STREAM.stop_stream()
        STREAM.close()
        PyAudio.terminate()


def sendColorCode(r, g, b, w):
    color_code = bytes("R%dG%dB%dW%dE" % (r, g, b, w), 'utf-8')
    # ! CANT HAVE DNS NAME HAS IP OR ELSE LATENCY IS UP THE ROOF
    CLIENT_SOCKET.sendto(color_code, ("192.168.1.156", ARDUINO_PORT_NUMBER))


def analyzeData(in_data):
    fourier = getFourierTransform(in_data, np.blackman)
    # * Remove the DC offset. Bare in mind that if u want to get the freq u have to do index + 1
    fourier = fourier[1:]

    r_band, g_band, b_band = getBands(fourier)
    avg_r_band, avg_g_band, avg_b_band, avg_volume = getAverages(
        r_band, g_band, b_band, fourier)
    r, g, b, w = mapAmplitudeToColorRange(
        255, avg_r_band, avg_g_band, avg_b_band, avg_volume)
    return validatedNumbers(255, r, g, b, w)


def getFourierTransform(in_data, window_function):
    fourier = np.abs(np.fft.rfft(in_data * window_function(len(in_data))))
    return fourier


def getBands(fourier):
    bass_band = fourier[:BASE_BAND_UPPER_LIMIT]
    midrange_band = fourier[BASE_BAND_UPPER_LIMIT:MIDRANGE_BAND_UPPER_LIMIT]
    upper_band = fourier[MIDRANGE_BAND_UPPER_LIMIT:UPPERRANGE_BAND_UPPER_LIMIT]

    return bass_band, midrange_band, upper_band


def getAverages(*args):
    return [np.average(arg) for arg in args]


def mapAmplitudeToColorRange(map_range, *args):
    return [round(map_range * (arg / MAX_AMP)) for arg in args]


def validatedNumbers(map_range, *args):
    return [max(0, min(map_range, arg)) for arg in args]


if __name__ == "__main__":
    try:
        while True:
            in_stream = readInputStream()
            data = np.frombuffer(in_stream, "int32")
            r, g, b, w = analyzeData(data)
            sendColorCode(r, g, b, w)
    except KeyboardInterrupt:
        CLIENT_SOCKET.close()
        closeInputStream()
        print()
        exit()
