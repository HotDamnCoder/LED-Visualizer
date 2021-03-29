import socket


class ArduinoSocket:
    def __init__(self, ip, port):
        try:
            self.ip = socket.gethostbyname(ip)
        except socket.error:
            raise Exception("Invalid ip address.")
        try:
            self.port = int(port)
        except ValueError:
            raise Exception("Invalid port number.")
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send(self, data):
        self.__socket.sendto(bytes(data, "utf-8"), (self.ip, self.port))
    
    def close(self):
        self.__socket.close()