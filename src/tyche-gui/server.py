# server program
from jsonrpclib.SimpleJSONRPCServer import SimpleJSONRPCServer
from jsonrpclib import Server
from functions import *


        self.send_response(200)

        # Override CORS
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "*")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(response.encode())

if __name__ == '__main__':  
    main()


