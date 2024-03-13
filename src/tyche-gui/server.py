#!/usr/bin/env python3

"""
Serve the JSON RPC endpoint for the Tyche solver
"""
import os
import multiprocessing
from http.server import BaseHTTPRequestHandler, SimpleHTTPRequestHandler, HTTPServer
from jsonrpcserver import dispatch
from functions import *
import logging
import argparse

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

class ContentHTTPServer(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        SimpleHTTPRequestHandler.end_headers(self)

def http_server():
    content_dir = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
    HTTPServer(('0.0.0.0', 8081), lambda *_ : ContentHTTPServer(*_, directory = content_dir)).serve_forever()

def main(no_content):
    logging.basicConfig(level=logging.DEBUG)
    if not no_content:
        #start local image server
        http_process = multiprocessing.Process(target=http_server)
        http_process.start()
    HTTPServer(('0.0.0.0', 8080), JSONRPCHTTPServer).serve_forever()

if __name__ == '__main__':  
    parser = argparse.ArgumentParser(
        prog="Tyche API Server",
        description="Server for Tyche simulation and optimization requests")

    parser.add_argument("--no_content", action='store_true', help= "Disable image content hosting")

    args = parser.parse_args()

    main(args.no_content)


