from DataAnalyzer import DataAnalyzer
from InputStream import pyaudioStream, alsaaudioStream
from ArduinoSocket import ArduinoSocket
from helperFunctions import exit, argumentParsing, getColorCode
import platform
# ! https://www.nti-audio.com/en/support/know-how/fast-fourier-transform-fft good resource about fft

if __name__ == "__main__":
    try:
        arduino_ip, arduino_port = argumentParsing()
        ARDUINO_SOCKET = ArduinoSocket(arduino_ip, arduino_port)
    except Exception as e:
        exit(e)

    os = platform.system()
    if os == "Windows":
        RECORDING_STREAM = pyaudioStream()
    elif os == "Linux":
        RECORDING_STREAM = alsaaudioStream()
    else:
        exit("OS not supported")
        
    # * Sets the variables associated with audio analysis
    max_amp = 10 ** (100 / 10)
    freq_resolution = RECORDING_STREAM.rate / RECORDING_STREAM.chunk_size

    r_band_limit = round(600 / freq_resolution)
    g_band_limit = round(2400 / freq_resolution)
    b_band_limit = round(9600 / freq_resolution)

    ANALYZER = DataAnalyzer(
        max_amp, [r_band_limit, g_band_limit, b_band_limit])

    print("Starting to record audio...")
    try:
        while True:
            data = RECORDING_STREAM.read()
            r, g, b, w = ANALYZER.analyzeData(data)
            ARDUINO_SOCKET.send(getColorCode(r, g, b, w))
    except KeyboardInterrupt:
        ARDUINO_SOCKET.send(getColorCode(0, 0, 0, 0))
        ARDUINO_SOCKET.close()
        RECORDING_STREAM.close()
        exit("")
