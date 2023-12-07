#!/usr/bin/env python3

from http.server import SimpleHTTPRequestHandler
import socketserver
import os
import sys

if len(sys.argv) > 1:
    os.chdir(sys.argv[-1])

PORT = 8000

class CORSRequestHandler(SimpleHTTPRequestHandler):
    def end_headers (self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', '*')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.send_header('Access-Control-Allow-Credentials', 'false')
        SimpleHTTPRequestHandler.end_headers(self)

with socketserver.TCPServer(("", PORT), CORSRequestHandler) as httpd:
    print("serving at port", PORT)
    httpd.serve_forever()
