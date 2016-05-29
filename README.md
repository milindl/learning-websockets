#Learning Websockets
This repository was originally made to learn about websockets. There was no better way than *implementing a websocket server* from scratch(since the client sided part is almost trivial). So I've implemented a chat server.

### Requirements
* python3
* any webserver, to host index.html
* a modern web-browser (tested on firefox 46 and chromium 50)
* Basic idea/experience using apache/http.server and understanding client/server relationships

### Usage
1. Change host in index.html to the IP "A" where your server.py is running.
2. Start hosting index.html on a web hosting server(IP "B"). You can use apache if you want, or simply do
```
$ cd directory_where_index.html_is
$ python3 -m http.server 8888
```
3. Start server.py
```
$ python3 server.py
```
3. Point as many web-browsers as you want towards the location of your server (the IP address IP "B")

Note: The IP/location of the WebSocket server and the WebHosting server are unrelated. However, in my testing process, I ran them both off the same machine, so both were localhost for me, with different port numbers.
So to re-iterate, the **host** in your index.html file point to the _IP address of the computer where server.py is running_ and your **browser address bar** points to the _IP address where your web-hosting server is running_.
To keep it simple, keep both on your own machine and replace both with localhost.


### Brief Explanation of the WebSocket Protocol

Refer to the actual [Internet Standards Track document][1] first.
So, here's how it works:

#### Handshake
This is the first step. The browser initiates the WebSocket connection by sending a request typically structured like so:
```
Host: location_of_server
User-Agent: Mozilla/5.0
Accept: text/html
Sec-WebSocket-Version: 13
Origin: location_of_client
Sec-WebSocket-Protocol: arbitrarily_named_protocol
Sec-WebSocket-Key: n6SorMqVHOdlOyQvgBYeRg==
Connection: keep-alive, Upgrade
Upgrade: websocket
```

This connection is supposed to be an HTTP 1.1 "Upgrade". All this means is that since this is based on HTTP, you need to send an HTTP request to initiate the whole thing.
The Sec-WebSocket-Protocol is also important since the server has to reply with the same protocol.
The Sec-WebSocket-Key is also important.
You need to SHA1 digest the Sec-WebSocket-Key to which a constant 258EAFA5-E914-47DA-95CA-C5AB0DC85B11 is appended, then encode it in base 64, then send it back. Apparently this is to make sure that the server isn't tricked by a nefarious client or whatever.

The response looks like so:
```
Connection: Upgrade
Sec-WebSocket-Accept: 8hq6y22P1VArkWL7LKm/dYtZ+NU=
Sec-WebSocket-Protocol: same_arbitrarily_named_protocol
Upgrade: websocket
```
It's fairly clear from the explanation above. Look how weird the Sec-WebSocket-Accept thing is-that's the b64 encoded, SHA1 digest of Sec-WebSocket-Key+that constant.

#### Sending: Frames
Since HTTP Client, Servers are really not cool with streams, we need to use something called frames. A frame is a bit of data with certain parameter appended in front of it to tell us how to interpret that data.
You should refer to the [actual document][1] for a better and a more confusing image of the frame, but I'll try to give a brief idea here.
A frame looks like so -
```
(fin-1)(rsv-3)(opcode-4)(mask-1)(payload_size-7)[optional - extended_payload_size] actual payload data
```
The number in front denotes the number of bits the information takes.
* ```fin``` : denotes whether the frame is self-contained(1 if it is), i.e. if it's the complete message you're sending. You can split your message across several frames. I have never needed to till now.  
* ```rsv``` : Three reserved bits. Best leave alone.
* ```opcode``` : denotes the kind of message. The most relevant ones are 0b0001 (text), 0b0010 (binary) and 0b1000 (close) in my code.
* ```mask``` : denotes whether the data is masked or not. When you send, this is usually 0, but data from the client *will be masked*. More in the next section.
* ```payload_size``` : payload size. Write the actual length here(in bytes). 2<sup>7</sup> gives us 127B as our maximum size, which isn't too much. However, it works slightly differently. If your size is between 0-125B, you write the size directly. If it is between 127B to 2<sup>16</sup>B, you write 126 in the payload_size field and utilize the extended_payload_size field. By using 127 instead of 126, you can go up to 2<sup>64</sup>B, which is usually sufficient. Refer to [this site](http://lucumr.pocoo.org/2012/9/24/websockets-101/) for a nice explanation.

#### Receiving: Unmasking

Unlike the server side, client sided messages have to be masked with a masking key that's given in the frame.
The masking key is a 4-byte key.
The unmasking looks like so:
```
masks = array of masks
indexFirstMask = index of first byte of mask in the masked_message
for i from indexFirstMask to length(masked_message)):
    j = i - indexFirstMask //j is the offset of the masked byte from where the mask starts
    unmasked_message.append(masked_message[i] XOR masks[j MOD 4])
```
Yeah. It has a MOD and a bitwise XOR in it. Confusing. Refer to the [this answer](http://stackoverflow.com/questions/8125507/how-can-i-send-and-receive-websocket-messages-on-the-server-side) for a very nice explanation of masking.

#### Closing
Closing is simple, however it's structured as a handshake.
```javascript
var ws = new WebSocket(host, protocol)
ws.close()
```

This sends a frame to the server with the opcode 0b1000. So if you get that, the you have to respond appropriately.

You need to send frame with the opcode 0b1000 back. The frame will look like so:
```
(1)(000)(1000)(0)(00000010) status_code_in_binary
```
They should be fairly obvious(look at the format I've given above).
The opcode is 0b1000, the length of the message is 2 bytes.
The message itself is an integer, a status code from 1000 to 1004, which denotes how the websocket was closed. 1000 is the normal closure. Note than you need to "pack" the integer into two separate bytes.


[1]:https://tools.ietf.org/html/rfc6455
