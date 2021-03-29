import sys
import getopt
import socket


def getColorCode(r, g, b, w):
    return "R%dG%dB%dW%dE" % (r, g, b, w)


def argumentParsing():
    ip = None
    port = None
    try:
        options, remainder = getopt.getopt(sys.argv[1:], "hp:", ["ip="])
        for opt, arg in options:
            if opt == "--ip":
                ip = arg
            elif opt == "-p":
                port = arg
            elif opt == '-h':
                exit("Script usage : <script_name> --ip <arduino_ip> -p <arduino_port>")
        if ip is None or port is None:
            raise Exception("Not enough arguments.")
    except getopt.GetoptError:
        raise Exception("Invalid arguments.")

    return ip, port


def exit(message):
    print(message)
    print("Exiting...")
    print("Have a nice day! :)")
    sys.exit()
