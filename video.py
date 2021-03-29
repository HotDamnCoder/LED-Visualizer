from math import sqrt
from PIL import ImageGrab
from ArduinoSocket import ArduinoSocket
from helperFunctions import exit, argumentParsing, getColorCode


def getAverageColorFromResizing(image):
    # * Downscales the image to 1x1 image with the LANCZOS method
    downscaled_image = image.resize((1, 1), ImageGrab.Image.LANCZOS)
    r, g, b = downscaled_image.load()[0, 0]
    # w = sqrt(0.241*(r**2) + 0.691*(g**2) + 0.068*(b**2))
    return r, g, b, 0


if __name__ == "__main__":
    try:
        arduino_ip, arduino_port = argumentParsing()
        ARDUINO_SOCKET = ArduinoSocket(arduino_ip, arduino_port)
    except Exception as e:
        exit(e)
        
    print("Starting to record screen...")
    try:
        while True:
            r, g, b, w = getAverageColorFromResizing(ImageGrab.grab())
            ARDUINO_SOCKET.send(getColorCode(r, g, b, w))
    except KeyboardInterrupt:
        ARDUINO_SOCKET.send(getColorCode(0, 0, 0, 0))
        ARDUINO_SOCKET.close()
        exit("")
