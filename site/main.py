#!/usr/bin/env python3
 
from http.server import BaseHTTPRequestHandler,HTTPServer, CGIHTTPRequestHandler

import cgitb; 

#to get it work, you should start this file and enter http://localhost:8000/articles in browser

if __name__ == '__main__':
	cgitb.enable()  

	server = HTTPServer
	handler = CGIHTTPRequestHandler
	server_address = ("", 8000)
	handler.cgi_directories = ["/"]
 
	httpd = server(server_address, handler)
	httpd.serve_forever()