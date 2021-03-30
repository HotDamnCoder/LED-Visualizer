import numpy as np
import platform


class InputStream():
    def __init__(self, chunk_size=1024, channels=1):
        pass

    def read(self):
        pass

    def close(self):
        pass


class alsaaudioStream(InputStream):
    # * Alsaaudio InputStream implementation
    def __init__(self, chunk_size=1024, channels=1):
        import alsaaudio
        self.chunk_size = chunk_size
        self.channels = channels
        self.rate = 44100
        self.stream = alsaaudio.PCM(type=alsaaudio.PCM_CAPTURE,
                                    mode=alsaaudio.PCM_NORMAL,
                                    rate=self.rate,
                                    channels=self.channels,
                                    format=alsaaudio.PCM_FORMAT_S32_LE,
                                    periodsize=self.chunk_size)

    def read(self):
        return np.frombuffer(self.stream.read()[1], "int32")

    def close(self):
        pass


class pyaudioStream(InputStream):
    # * PyAudio InputStream implementation
    def __init__(self, chunk_size=1024, channels=1):
        import pyaudio

        def findStereoMix(PyAudio):
            for i in range(PyAudio.get_device_count()):
                host_api = PyAudio.get_host_api_info_by_index(i)
                for j in range(host_api['deviceCount']):
                    api_device = PyAudio.get_device_info_by_host_api_device_index(
                        i, j)
                    if api_device['name'] == "Stereo Mix":
                        return api_device
            return None
        self.chunk_size = chunk_size
        self.channels = channels
        self.PyAudio = pyaudio.PyAudio()
        WASAPI_info = self.PyAudio.get_host_api_info_by_type(pyaudio.paWASAPI)

        if 'defaultOutputDevice' in WASAPI_info.keys():
            recording_device = self.PyAudio.get_device_info_by_index(
                WASAPI_info['defaultOutputDevice'])
        else:
            print("No WASAPI compatible device.")
            print("Using Stereo Mix.")
            recording_device = findStereoMix(self.PyAudio)
            if recording_device is None:
                raise Exception("Didn't find Stereo Mix.")

        device_index = recording_device['index']
        self.rate = int(recording_device['defaultSampleRate'])
        self.stream = self.PyAudio.open(format=pyaudio.paInt32,
                                        channels=self.channels,
                                        rate=rate,
                                        input=True,
                                        frames_per_buffer=self.chunk_size,
                                        input_device_index=device_index,
                                        as_loopback=True)

    def read(self):
        return np.frombuffer(self.stream.read(self.chunk_size), "int32")

    def close(self):
        self.stream.stop_stream()
        self.stream.close()
        self.PyAudio.terminate()
