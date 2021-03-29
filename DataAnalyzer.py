import numpy as np


class DataAnalyzer:
    last_data_point = None

    def __init__(self, max_amp, band_end_points, windowing_function=np.blackman, exp_alpha=0.6):
        self.windowing_function = windowing_function
        self.alpha = exp_alpha
        self.r_band, self.g_band, self.b_band = band_end_points
        self.max_amp = max_amp

    def __average(self, *args):
        # * Averages arguments
        return [np.average(arg) for arg in args]

    def __mapToColorRange(self, *args):
        # * Maps arguments to range -255 to 255 (but its probably 0 - 255 because negative number come rarely)
        return [round(255 * (arg / self.max_amp)) for arg in args]

    def __validatedNumbers(self, *args):
        # * Checks if arguments are in range 0 - 255
        return [max(0, min(255, arg)) for arg in args]

    def __expFilter(self, data):
        # * A Simple exponential smoothening filter
        if self.last_data_point is None:
            self.last_data_point = data[0]

        filtered_data = [self.alpha * data[i] + (1 - self.alpha) * data[i-1]
                         if i != 0 else self.last_data_point for i in range(len(data))]

        return filtered_data

    def __getFourierTransform(self, in_data):
        # * Gets the fourier transform of incoming signal after applying a windowing function (default: blackman)
        fourier = np.abs(np.fft.rfft(
            in_data * self.windowing_function(len(in_data))))
        return fourier

    def __getBands(self, fourier):
        # * Distributes fourier values to 3 bands which map to r, g, b
        bass_band = fourier[:self.r_band]
        midrange_band = fourier[self.r_band:self.g_band]
        upper_band = fourier[self.g_band:self.b_band]

        return bass_band, midrange_band, upper_band

    def analyzeData(self, in_data):
        filtered_data = self.__expFilter(in_data)
        self.last_data_point = in_data[-1]
        fourier = self.__getFourierTransform(filtered_data)

        # * Remove the DC offset. Bare in mind that if u want to get the freq u have to do index + 1
        fourier = fourier[1:]

        r_band, g_band, b_band = self.__getBands(fourier)
        r_band, g_band, b_band, avg_volume = self.__average(
            r_band, g_band, b_band, fourier)

        r, g, b, w = self.__mapToColorRange(
            r_band, g_band, b_band, avg_volume)

        return self.__validatedNumbers(r, g, b, w)
