_NB: There have been certain changes after I refactored my code. Go to the old master branch around 6 commits before this to view the old code. The instructions about the actual protocol still holds though._

# Learning Websockets
This repository was originally made to learn about websockets. There was no better way than *implementing a websocket server* from scratch(since the client sided part is almost trivial). So I've implemented a chat server.

Apologies for grammatical and spelling errors.

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

So to re-iterate, the **host** in your index.html file points to the _IP address of the computer where server.py is running_ and your **browser address bar** points to the _IP address where your web-hosting server is running_.
To keep it simple, keep both on your own machine and replace both with localhost.


### Brief Explanation of the WebSocket Protocol

Refer to the writeup at [http://milindl.org/writeups.html](http://milindl.org/writeups.html)
