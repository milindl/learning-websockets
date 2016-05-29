import socket, hashlib, base64, threading

class Serv:
    def __init__(self, host='0.0.0.0', port = 7000):
        self.ssock = None
        self.host = host
        self.port = port
        self.sent_q = []
        self.sock_list={}
        self.sock_list_lock = threading.Lock()
        self.sent_q_lock = threading.Lock()

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
Sec-WebSocket-Protocol: chat\r
Sec-WebSocket-Accept: '''
        reply=reply+websocket_accepted_key+"\r\n\r\n"
        sock.send(reply.encode())

    def send_data(self, data, sock):                   # Actual low level sender function (topmost stack)
        '''
        Prepare the headers and send the message. The sock in the params in temporary. Final solution is to use send queue
        '''
        data = data.encode('utf-8')
        payload=bytearray()
        length = len(data)
        s1=0b10000001
        #Flg:fin,rsv1,rsv2,rsv3,opcode
        s2=0b0
        # flg:mask
        #Possible thingies:
        #   Length less than 125
        #   Length more than 125 but less than 16 bit
        #   Length more than 16bit(rare)
        payload.append(s1)
        if length<=125:
            payload.append(s2+length)
        elif length.bit_length()<=16:
            payload.append(s2+126)
            import struct
            payload.extend(struct.pack("!H", length))  # This tricky bit changes the length 2 byte int to 2 bytes to extend the barray
        elif length.bit_length()<=64:
            payload.append(s2+127)
            import struct
            payload.extend(struct.pack("!Q", length))  # This changes int->8bytes to add to the bytearray
        # print(payload)
        payload.extend(data)
        # print(payload)
        sock.send(payload)

    def sent_q_clearer(self):                          # This method is a testing only method.
        '''
        Thread to monitor send q and send the requisite messages
        '''
        while True:
            if len(self.sent_q) == 0:
                continue
            with self.sent_q_lock:
                for message in self.sent_q:
                    for socket in self.sock_list:
                        self.send_data(message, socket)
                        print("Sending to all")
                    self.sent_q.remove(message)

    def listen(self, sock):
        #This is a standard listener thread
        while True:
            d = sock.recv(1024)
            secondByte = d[1]
            lg = secondByte & 127
            indexFirstMask = 2
            if lg == 126:
                indexFirstMask=4
            if lg == 127:
                indexFirstMask=10
            masks = d[indexFirstMask:indexFirstMask+4]
            indexFirstDataByte = indexFirstMask + 4
            decoded = bytearray()
            # decoded.length = bytes.length - indexFirstDataByte
            for i in range(indexFirstMask,len(d)):
                decoded.append(d[i] ^ masks[(i-indexFirstMask) % 4])
            # To handle socket specific cases, I need to deal with it here and now.
            # Case: first message
            if decoded.decode()[4:10]=="/NAME ":
                value = decoded.decode()[10:]
                if value in self.sock_list.values():
                    self.send_data("Please do NOT repeat usernames. Choose another one.")
                    continue
                with self.sent_q_lock:
                    self.sent_q.append("Name change: "+self.sock_list[sock]+" -> "+value)
                self.sock_list[sock] = value
                continue
            #Case: closing frame sent
            if d[0]==0x88:
                self.close_socket(sock)
                return
            with self.sent_q_lock:
                self.sent_q.append(self.sock_list[sock] + ":" + decoded.decode())

    def close_socket(self, sock, code=1000):
        '''
        Actually closes that socket with that status code
        Usage: self.close(sock, code=1000)
        '''
        s1 = 0b10001000
        s2 = 0b00000010
        payload = bytearray()
        payload.append(s1)
        payload.append(s2)
        import struct
        payload.extend(struct.pack("!H", code))
        try:
            sock.send(payload)
            sock.close()
        finally:
            with self.sock_list_lock:
                self.sock_list.pop(sock)

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
        user_counter = 0
        self.ssock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ssock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.ssock.bind((self.host,self.port))
        self.ssock.listen(1)
        threading.Thread(target=self.sent_q_clearer).start()
        while True:
            conn, add = self.ssock.accept()
            self.handshake(conn)
            with self.sock_list_lock:
                self.sock_list[conn] = "user" + str(user_counter)
            with self.sent_q_lock:
                self.sent_q.append('New user ' + self.sock_list[conn] +" has joined.")
            user_counter+=1
            threading.Thread(target=self.listen, args=(conn,)).start()
        self.ssock.close()


Serv().start()
