import sys
import getopt
import socket
from math import sqrt
from PIL import ImageGrab
from audio import CLIENT_SOCKET, sendColorCode, exit


def getAverageColorFromResizing(image):
    # * Downscales the image to 1x1 image with the LANCZOS method
    downscaled_image = image.resize((1, 1), ImageGrab.Image.LANCZOS)
    r, g, b = downscaled_image.load()[0, 0]
    # w = sqrt(0.241*(r**2) + 0.691*(g**2) + 0.068*(b**2))
    return r, g, b, 0


if __name__ == "__main__":
    ARDUINO_IP = None
    ARDUINO_PORT = None
    try:
        options, remainder = getopt.getopt(sys.argv[1:], "hp:", ["ip="])
        for opt, arg in options:
            if opt == "--ip":
                try:
                    ARDUINO_IP = socket.gethostbyname(arg)
                except socket.error:
                    exit("Invalid ip address.")
            elif opt == "-p":
                try:
                    ARDUINO_PORT = int(arg)
                except ValueError:
                    exit("Invalid port number.")
            elif opt == '-h':
                exit("Script usage : <script_name> --ip <arduino_ip> -p <arduino_port>")
    except getopt.GetoptError:
        exit("Invalid arguments.")

    if ARDUINO_IP is None or ARDUINO_PORT is None:
        exit("Not enough arguments.")

    print("Starting to record screen...")
    try:
        while True:
            r, g, b, w = getAverageColorFromResizing(ImageGrab.grab())
            sendColorCode(ARDUINO_IP, ARDUINO_PORT, (r, g, b, w))
    except KeyboardInterrupt:
        CLIENT_SOCKET.close()
        exit("")
