import numpy
import pyaudio
import wave
import matplotlib.pyplot as plt
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = 15
WAVE_OUTPUT_FILENAME = "output.wav"

p = pyaudio.PyAudio()
spe = p.get_device_info_by_index(2)
stream = p.open(format=FORMAT,
                channels=2,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK,
                input_device_index = 2)

print("* recording")

frames = []
datas = []
for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    frames.append(data)
    what = numpy.frombuffer(data, dtype=numpy.int16)
    datas.extend(what)



plt.plot(datas)
plt.show()
stream.stop_stream()
stream.close()
stream.stop_stream()
stream.close()
p.terminate()
print("* done recording")
wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
wf.setnchannels(CHANNELS)
wf.setsampwidth(p.get_sample_size(FORMAT))
wf.setframerate(RATE)
wf.writeframes(b''.join(frames))
wf.close()
print ( "done")
