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

    RATE = 44100
    CHANNELS = 1
    FORMAT = alsaaudio.PCM_FORMAT_S16_LE
    MIN_FREQ_BAND = RATE / CHUNK_SIZE

    STREAM = alsaaudio.PCM(type=alsaaudio.PCM_CAPTURE,
                           mode=alsaaudio.PCM_NORMAL,
                           rate=RATE,
                           channels=CHANNELS,
                           format=alsaaudio.PCM_FORMAT_S16_LE,
                           periodsize=CHUNK_SIZE)
elif CURRENT_OS == 'Windows':
    import pyaudio

    PyAudio = pyaudio.PyAudio()
    WASAPI_info = PyAudio.get_host_api_info_by_type(pyaudio.paWASAPI)

    try:
        default_WASAPI_output = PyAudio.get_device_info_by_index(
            WASAPI_info['defaultOutputDevice'])
    except KeyError:
        print("No WASAPI compatible device!")
        # TODO: Add support for stero mix maybe
        exit()

    DEVICE_INDEX = default_WASAPI_output['index']
    RATE = int(default_WASAPI_output['defaultSampleRate'])
    CHANNELS = 1
    FORMAT = pyaudio.paInt16
    STREAM = PyAudio.open(format=FORMAT,
                          channels=CHANNELS,
                          rate=RATE,
                          input=True,
                          frames_per_buffer=BUFFER,
                          input_device_index=DEVICE_INDEX)
else:
    print("OS not supported!")
    exit()


def getFourierTransform(in_data):
    data = np.frombuffer(in_data, "int16")
    fourier = np.abs(np.fft.rfft(data))
    return fourier


def analyzeData(in_data):
    fourier = getFourierTransform(in_data)


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
            analyzeData(in_data)
            sendColorCode(255, 255, 255)
    except KeyboardInterrupt:
        CLIENT_SOCKET.close()
        print()
        exit()

