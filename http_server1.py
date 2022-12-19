from logging.handlers import SocketHandler
import socket
import sys
from os.path import exists

not_found_err = "HTTP/1.1 404 Not Found \n\n The file you requested was not found on the server! \n\n"
forbidden_err = "HTTP/1.1 403 Forbidden \n\n You are not allowed to access the content of this file.\n\n"
success_response = "HTTP/1.1 200 OK \n\n"
listen_ip_str = "Listening for all IP addresses on port "

def generateSocket(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(("",port))
    except Exception:
        print(Exception, sys.stderr,)
        sys.exit(-1)
    return sock

def listen(sock,port):
    def parseHtmFile(name):
        name = name.lstrip("/")
        try:
            path = open(name)
            resp = path.read()
            path.close()
        except:
            return '404'
        return resp

    sock.listen(1)
    print(listen_ip_str + str(port))

    while True:
        client, _ = sock.accept()
        request = client.recv(2048).decode().split("\n")[0].split(" ")[1]
        fileType = request.split(".")[1]
        fileVal = parseHtmFile(request)
        if("404" == fileVal):
            resp = not_found_err
        elif(fileType != "htm" and fileType != "html"):
            if(exists(request.lstrip("/"))):
                resp = forbidden_err
        else:
            resp = success_response + fileVal + "\n\n"
        resp = bytes(resp,'utf-8')
        client.sendall(resp)
        client.close()

def main(port):
    sock = generateSocket(port)
    listen(sock, port)

if __name__ == "__main__":
    port = int(sys.argv[1])
    main(port)