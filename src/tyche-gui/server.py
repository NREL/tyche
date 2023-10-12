#!/usr/bin/env python3

"""
Serve the JSON RPC endpoint for the Tyche solver
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
from jsonrpcserver import dispatch
from functions import *
import logging

class JSONRPCHTTPServer(BaseHTTPRequestHandler):
    def do_POST(self):
        request = self.rfile.read(int(self.headers["Content-Length"])).decode()
        response = dispatch(request)

        self.send_response(200)

        # Override CORS
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "*")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(response.encode())

    def do_OPTIONS(self):
        # Preflight probe response

        self.send_response(204)

        # Override CORS
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "*")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Access-Control-Max-Age", "86400")
        self.end_headers()

def main():
    logging.basicConfig(level=logging.DEBUG)
    HTTPServer(('localhost', 8080), JSONRPCHTTPServer).serve_forever()

if __name__ == '__main__':  
    main()


