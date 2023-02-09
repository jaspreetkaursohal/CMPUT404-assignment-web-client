#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    #returning the code for the call
    def get_code(self, data):
        return(int(data[0].split(" ")[1]))
        
    #we dont really use this anywhere as far as I can see but returns headers?
    def get_headers(self,data):
        return data.split("\r\n")

    #return body of url
    def get_body(self, data):
        return data[1]
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    #gets the hostname, path and port from the url
    def getURLData(self,url):
        url_data = urllib.parse.urlparse(url)
        hostname = url_data.hostname
        path = url_data.path
        port = url_data.port
        return(hostname, path, port)

    def GET(self, url, args=None):
        hostname, path, port = self.getURLData(url)
        #if no port is assigned, make default port 80
        if port == None:
            port = 80

        if path == '':
            path="/"

        #Connect to hostname and port specified
        self.connect(hostname, port)

        #Form the request to be sent
        request = "GET " + path + " HTTP/1.1\r\nHost: " + hostname + "\r\n"
        request += "Accept: */*\r\nConnection: close\r\n\r\n"
        self.sendall(request)

        socket_data = self.recvall(self.socket)
        code = self.get_code(socket_data.split('\r\n'))
        body = self.get_body(socket_data.split('\r\n\r\n'))
        self.close()
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        hostname, path, port = self.getURLData(url)
        if port == None:
            port = 80

        if path == '':
            path="/"
        self.connect(hostname, port)
        request = "POST " + path + " HTTP/1.1\r\nHost: " + hostname + "\r\n"
        if not args:
            arg = ""
        else:
            arg = urllib.parse.urlencode(args)
        request += "Content-Type: application/x-www-form-urlencoded\r\nContent-Length: " + str(len(arg)) + "\r\nConnection: close\r\n\r\n"
        request += arg
        self.sendall(request)
        socket_data = self.recvall(self.socket)
        code = self.get_code(socket_data.split('\r\n'))
        body = self.get_body(socket_data.split('\r\n\r\n'))

        self.close()
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
