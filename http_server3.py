import socket
import sys
import json

product_str = "/product"
not_found_err = "HTTP/1.1 404 Not Found \n\n The resource you requested was not found on the server!\n\n"
not_a_number = "HTTP/1.1 400 Bad Request \n\n Your input probably wasn't a number!\n\n"
success_response = "HTTP/1.1 200 OK \nContent-Type: application/json \n\n"

def generateSocket(port):
    skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        skt.bind(("", port))
    except Exception:
        print(Exception, sys.stderr,)
        sys.exit(-1)
    return skt

def listenToRequests(skt,port):
    def clentSend(str, client):
        resp = str
        client.sendall(bytes(resp,'utf-8'))
        client.close()

    def clentSendShutDwn(str, client):
        client.sendall(str)
        client.shutdown(1)

    def getEndResponse(op, pJson, req):
        pJson['operands'] = []       
        pJson['operands'].append(float(op.split("=")[1]))
        pJson['operation'] = req[0].split(" ")[1].lstrip("/")
        pJson['result'] = product
        endResponseJson = json.dumps(pJson)
        return success_response + endResponseJson + "\n\n"

    def splitSpace(str):
        return str.split(" ")

    skt.listen(1)
    print("Listening for all IP addresses on port " + str(port))

    while True:
        client, _ = skt.accept()
        request = client.recv(2048).decode().split("\n")[0].split("?")
        print(request)
        if(splitSpace(request[0])[1] != product_str):
            clentSend(not_found_err, client)
            continue
        else:
            responseProductJson = {}
            operandList = splitSpace(request[1])[0].split("&")
            product = 1
            print(operandList)
            for operand in operandList:
                try:
                    number = float(operand.split("=")[1])
                    product *= number
                except Exception:
                    clentSend(not_a_number, client)
                    break
                else:
                    resp = getEndResponse(operand, responseProductJson, request)
                    resp = bytes(resp, 'utf-8')
        clentSendShutDwn(resp, client)

def main(port):
    skt = generateSocket(port)
    listenToRequests(skt, port)

if __name__ == "__main__":
    port = int(sys.argv[1])
    main(port)