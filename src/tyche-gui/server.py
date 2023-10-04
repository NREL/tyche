# server program
from jsonrpclib.SimpleJSONRPCServer import SimpleJSONRPCServer
from jsonrpclib import Server
from functions import *


def main():
    server = SimpleJSONRPCServer(('localhost', 1080))
    server.register_function(get_technology)
    server.register_function(evaluate_with_slider_input)
    server.register_function(evaluate_without_slider_input)
    print("Start server")
    server.serve_forever()
    server.shutdown()


if __name__ == '__main__':  
    main()


