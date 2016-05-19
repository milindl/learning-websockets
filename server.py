import socket, hashlib, base64

class Serv:
    def __init__(self, host='127.0.0.1', port = 7000):
        self.ssock = None
        self.host = host
        self.port = port

    def handshake(self,sock):
        '''
        Recieves headers, parses headers and sends a response appropriate.
        '''
        req = sock.recv(4096).decode("utf-8")
        h = self.parse_headers(req)
        websocket_accepted_key= self.hashin_shit(h["Sec-WebSocket-Key"])
        reply = '''
HTTP/1.1 101 Switching Protocols\r
Upgrade: websocket\r
Connection: Upgrade\r
Sec-WebSocket-Accept: '''
        reply=reply+websocket_accepted_key+"\r\n\r\n"
        sock.send(reply.encode())
        print(reply)
        sock.sendall('')

    def parse_headers(self,headers):
        '''
            Usage:
            parse_headers(headers)
            Returns a dictionary of headers
        '''
        parsed_headers = {}
        lines = headers.split("\n")
        for line in lines:
            k = line.split(":")
            if(len(k)<2): continue
            parsed_headers[k[0].strip()] = "".join([str(k[i]).strip() for i in range(1,len(k))])
        return parsed_headers


    def hashin_shit(self, key):
        '''
        Makes the requisite hash from given key as specced in the protocol
        '''
        GUID = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
        key = key.strip()+GUID.strip()
        hasher = hashlib.sha1()
        hasher.update(key.encode())
        to_return = base64.b64encode(hasher.digest())
        return (to_return.decode('utf-8'))

    def start(self):
        self.ssock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ssock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.ssock.bind((self.host,self.port))
        self.ssock.listen(1)
        while True:
            conn, add = self.ssock.accept()
            self.handshake(conn)
        self.ssock.close()


Serv().start()
