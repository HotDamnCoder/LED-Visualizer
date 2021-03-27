from math import sqrt
from PIL import ImageGrab
from audio import CLIENT_SOCKET, sendColorCode, argumentParsing, exit


def getAverageColorFromResizing(image):
    # * Downscales the image to 1x1 image with the LANCZOS method
    downscaled_image = image.resize((1, 1), ImageGrab.Image.LANCZOS)
    r, g, b = downscaled_image.load()[0, 0]
    # w = sqrt(0.241*(r**2) + 0.691*(g**2) + 0.068*(b**2))
    return r, g, b, 0


if __name__ == "__main__":
    ARDUINO_IP, ARDUINO_PORT = argumentParsing()

    print("Starting to record screen...")
    try:
        while True:
            r, g, b, w = getAverageColorFromResizing(ImageGrab.grab())
            sendColorCode(ARDUINO_IP, ARDUINO_PORT, (r, g, b, w))
    except KeyboardInterrupt:
        CLIENT_SOCKET.close()
        exit("")
