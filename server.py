#!/usr/bin/python3

from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import threading
import os
import socket
import fcntl
import struct

def get_ip_address(NICname):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack('256s', NICname[:15].encode("UTF-8"))
        )[20:24])
    except:
      return None

def all_addresses():
    addresses = []
    for ix in socket.if_nameindex():
      ip = get_ip_address(ix[1])
      if ip and ip != '127.0.0.1':
          addresses.append(ip)
    return addresses

myname = socket.gethostname()
myaddresses = all_addresses()

msg = ""
include_ip = False

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        global msg
        global include_ip
        # curl http://<ServerIP>/index.html
        if self.path == "/":
            # Respond 200.
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write("{}\n".format(msg).encode('utf-8'))
            if include_ip:
                self.wfile.write("Your IP Address is: {}\n".format(self.client_address[0]).encode('utf-8'))
        else:
            self.send_response(404)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"404 Not Found\n")
        return

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    "threaded http server"

if __name__ == "__main__":
    msg = os.environ.get('WEB_MESSAGE', "Hello there.")
    msg = msg.replace("[hostname]", myname)
    msg = msg.replace("[addresses]", ",".join(myaddresses))
    include_ip = os.environ.get('WEB_MESSAGE_INCLUDE_IP', True)
    serverPort = int(os.environ.get('WEB_SERVER_PORT', '80'))
    print("Loaded Web Message: {}".format(msg))
    webServer = ThreadedHTTPServer(('0.0.0.0', serverPort), Handler)
    print("Server started http://%s:%s" % ('0.0.0.0', serverPort))
    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass
    webServer.server_close()
    print("Server stopped.")
