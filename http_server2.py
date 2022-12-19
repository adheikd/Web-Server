import select
import socket
import sys
import queue
from os.path import exists

resQ = {}
listinput = []
listoutput = []

def createsocket(port):
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.setblocking(0)
    soc.bind(("",port))
    soc.settimeout(5)
    listinput.append(soc)
    return soc

def checkMessage(content):
    mapContent = {
        "notfound": "HTTP/1.1 404 Not Found\n\n"\
            "The file you requested was not found\n\n",
        "html": "HTTP/1.1 404 Not Found\n\n"\
            "The file you requested was not found\n\n",
        "200": "HTTP/1.1 200 OK \n\n"
    }

    return mapContent[content]

def makesocketlisten(soc,port):
    print('Listening for multiple connections on port ' + str(port))
    soc.listen(5)
    while listinput:
        print('Waiting for the next event')
        rinputlist, woutputlist, elist = select.select(listinput,listoutput,listinput)
        print(rinputlist)
        print(woutputlist)
        for in_iterator in rinputlist:
            if in_iterator is soc:
                print("WE ARE CHECKING IF THE SERVER IS WAITING")
                connect, clnt_address = in_iterator.accept()
                print('Getting....connection from', clnt_address)
                connect.setblocking(0)
                listinput.append(connect)
                resQ[connect] = queue.Queue()
            else:
                req = in_iterator.recv(1024)
                if req:
                    print('Request...received {!r} from {}'.format(req, in_iterator.getpeername()))
                    resQ[in_iterator].put(req)
                    if in_iterator not in listoutput:
                        listoutput.append(in_iterator)
                else:
                    print('Connetions will be closing', clnt_address)
                    if listinput in listoutput:
                        listoutput.remove(in_iterator)
                    listinput.remove(in_iterator)
                    del resQ[in_iterator]
                    in_iterator.close()
        for out_iterator in woutputlist:
            try:
                Msge = resQ[out_iterator].get_nowait()
            except queue.Empty:
                print('  ', out_iterator.getpeername(), 'queue empty')
                listoutput.remove(out_iterator)
            else:
                Msge = Msge.decode().split("\n")[0].split(" ")[1]
                try:
                    ftype = Msge.split(".")[1]
                except Exception:
                    ftype = "htm"
                else:
                    fcontent = pullandreadfile(Msge)
                    if(fcontent == "notfound"):
                        Msge = checkMessage(fcontent)
                    elif(ftype!="htm" and ftype!="html"):
                        if(exists(Msge.lstrip("/"))):
                            Msge = checkMessage("html")
                    else:
                        Msge = checkMessage("200") + fcontent + "\n\n"
                    Msge = bytes(Msge,'utf-8')
                    print('Message being sent {!r} to {}'.format(Msge,out_iterator.getpeername()))
                    slength = out_iterator.sendall(Msge)
                    out_iterator.shutdown(1)
                    
        for e_iterator in elist:
            print('The exception code is', e_iterator.getpeername())
            listinput.remove(e_iterator)
            if e_iterator in listoutput:
                listoutput.remove(e_iterator)
            e_iterator.close()
            del resQ[e_iterator]

def pullandreadfile(fname):
    fname = fname.lstrip("/")
    exists(fname)
    try:
        fp = open(fname)
        res = fp.read()
        fp.close()
    except:
        return "notfound"
    return res

def main(port):
    soc = createsocket(port)
    makesocketlisten(soc,port)

port = int(sys.argv[1])
main(port)