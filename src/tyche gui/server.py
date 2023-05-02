# server program
from jsonrpclib.SimpleJSONRPCServer import SimpleJSONRPCServer

def findlen(*args):

	res = []
	for arg in args:
		try:
			lenval = len(arg)
		except TypeError:
			lenval = None
		res.append((lenval, arg))
	return res

def main():
	server = SimpleJSONRPCServer(('localhost', 1080))
	server.register_function(findlen)
	print("Start server")
	server.serve_forever()
	server.shutdown()


if __name__ == '__main__':  
    main()


