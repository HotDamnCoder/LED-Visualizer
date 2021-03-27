# LED-Visualizer
A simple LED-visualizer program written in Python which communicates its information with Arduino over WiFi wtih UDP protocol.

Supports audio (audio.py) and video (video.py) visualization for RGBW non-adressable LED strip.

Dependencies:
- Numpy
- PyAudio (for WASAPI as_loopback feature must have a special version of [PyAudio](https://github.com/intxcc/pyaudio_portaudio))
- AlsaAudio (if you're on linux)
- Python Image Library (PIL)

Usage : <script_name> --ip <arduino_ip> -p <arduino_port>

Note : IP argument can be also a mDNS or DNS name
