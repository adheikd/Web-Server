import socket
import sys

one_one = " HTTP/1.1\r\nHost: "
accept_str = "\r\nAccept: */*\r\n\r\n"
get_str = "GET "
error_log = "errors.log"
buff_size = 2048

def getInt(value):
    return int(value)

def getBuffer(socket):
    return socket.recv(buff_size)

def sendReq(socket, host, resource, port):
    headers = get_str + resource + one_one + host + accept_str
    socket.connect((host, port))
    socket.sendall(headers.encode())
    return parseResponse(socket)

def parseResponse(socket):
    fileError = open(error_log, "w")
    response = b''
    while True:
        buffer = getBuffer(socket)
        print(buffer, file = fileError,)
        response += buffer
        if len(buffer) < buff_size: 
            if (buffer.decode().find("</html>") != -1 or buffer.decode().find("</HTML>") != -1):
                break
    fileError.close()
    return response.decode("utf-8", "ignore")

def getLocHeader(response):
    iter = response.split("\n\n")[0].count("\n")
    headers = {}
    for i in range(1, getInt(iter)/2):
        headers[response.split("\n")[i].split(":")[0].strip()] = response.split("\n")[i].split(":")[1:]
    if 'Location' in headers:
        headers['Location'] = (headers['Location'][0] + ":" + headers['Location'][1]).strip()
        return headers, headers['Location']
    return headers

def sysExit(headers, response):
    if "Content-Type" not in headers:
        try:
            print(response.split("\r\n\r\n")[1].split("<body")[1].split("</body>")[0])
            return(sys.exit(0))
        except:
            return(sys.exit(-1))
    return(sys.exit(-1))

def main(host):
    port = host[2]
    host = host[0]
    statusCode = 0
    itr = 0
    headers = {}
    response = ''

    def processStatusCode(statusCode,response):
        host = "testHost"
        headers = getLocHeader(response)
        if (statusCode in ['301', '302']):
            host = getLocHeader(response)
            print("Redirected to", None, sys.stderr)
            host = processHost(host[1])
        return statusCode, host, headers

    while(statusCode in ['301', '302', '0'] or itr > 10):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(True)
        response = sendReq(socket, host[0], host[1], port)
        statusCode, host, headers = processStatusCode(response.split(" ")[1], response)
        itr = itr + 1
        socket.close()

    if "Content-Type" in headers and headers['Content-Type'][0].strip().split(";")[0] == "text/html":
        if "<body " in response.split("\r\n\r\n")[1] or "<body>" in response.split("\r\n\r\n")[1]: 
            print(response.split("\r\n\r\n")[1].split("<body")[1].split("</body>")[0])
            return(sys.exit(0))

    return sysExit(headers, response)
    

def processHost(mainaddr):
    if("https://" in mainaddr):
        print("https url received, exiting", sys.stderr,)
        sys.exit(-1)
    port = 80
    if ":" in mainaddr.split("http://")[0]:
        mainaddr = mainaddr.split(":")[0]
        port = mainaddr.split(":")[1]
    mainaddr = mainaddr.lstrip("http://")
    if len(mainaddr.split("/")) > 1 and mainaddr.split("/")[1] != "":
        resource = "/" + mainaddr.split("/")[1]
    else:
        resource = "/"
    return mainaddr.split("/")[0], resource.rstrip(), port

if __name__ == "__main__":
    host = processHost(sys.argv[1])
    main(host)
