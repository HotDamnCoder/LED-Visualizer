import numpy as np
import platform


class InputStream():
    def __init__(self, chunk_size=1024, channels=1):
        self.chunk_size = chunk_size
        self.channels = channels

        os = platform.system()
        # * Initializes the stream based on OS
        if os == "Linux":
            import alsaaudio
            self.rate = 44100
            self.stream = alsaaudio.PCM(type=alsaaudio.PCM_CAPTURE,
                                        mode=alsaaudio.PCM_NORMAL,
                                        rate=self.rate,
                                        channels=self.channels,
                                        format=alsaaudio.PCM_FORMAT_S32_LE,
                                        periodsize=self.chunk_size)
            self.__class__ = alsaaudioStream

        elif os == "Windows":
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

            PyAudio = pyaudio.PyAudio()
            WASAPI_info = PyAudio.get_host_api_info_by_type(pyaudio.paWASAPI)

            if 'defaultOutputDevice' in WASAPI_info.keys():
                recording_device = PyAudio.get_device_info_by_index(
                    WASAPI_info['defaultOutputDevice'])
            else:
                print("No WASAPI compatible device.")
                print("Using Stereo Mix.")
                recording_device = findStereoMix(PyAudio)
                if recording_device is None:
                    raise Exception("Didn't find Stereo Mix.")

            device_index = recording_device['index']
            self.rate = int(recording_device['defaultSampleRate'])
            self.stream = PyAudio.open(format=pyaudio.paInt32,
                                       channels=self.channels,
                                       rate=rate,
                                       input=True,
                                       frames_per_buffer=self.chunk_size,
                                       input_device_index=device_index,
                                       as_loopback=True)
            self.__class__ = pyaudioStream

        else:
            raise Exception("OS not supported.")

    def read(self):
        pass

    def close(self):
        pass


class alsaaudioStream(InputStream):
    # * Alsaaudio InputStream implementation
    def read(self):
        return np.frombuffer(self.stream.read()[1], "int32")

    def close(self):
        pass


class pyaudioStream(InputStream):
    # * PyAudio InputStream implementation
    def read(self):
        return np.frombuffer(self.stream.read(self.chunk_size), "int32")

    def close(self):
        self.stream.stop_stream()
        self.stream.close()
        PyAudio.terminate()
