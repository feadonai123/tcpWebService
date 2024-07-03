import socket
import _thread

import FileService

PORT = 1234
HOST = "127.0.0.1"

class HTTPResponse:
  def __init__(self, status, content, content_type="text/html"):
    self.status = status
    self.content = content
    self.content_type = content_type
    
  def __str__(self):
    return f"HTTP/1.1 {self.status}\nContent-Type: {self.content_type}\n\n{self.content}"
    
  def __bytes__(self):
    return str(self).encode()
  
  
class HTTPRequest:
  
  def __init__(self, request):
    self.request = request
    self.method = None
    self.path = None
    self.body = None
    self.__parse()
    
  def __parse(self):
    lines = self.request.split(b"\n")
    self.method, self.path, _ = lines[0].split(b" ")
    self.path = self.path.decode()
    self.method = self.method.decode()
    self.type = self.path.split(".")[-1]
    self.body = lines[-1]
    
  def __str__(self):
    return f"Method: {self.method}\nPath: {self.path}\nBody: {self.body}"
    
  def __bytes__(self):
    return str(self).encode()


class TCPServer:
  
  PUBLIC_DIR = "./tcpWeb/public"
  threadCount = 0
  
  def __init__(self, showLog=True):
    self.server = socket.socket(family=socket.AF_INET,type=socket.SOCK_STREAM)
    self.lock = _thread.allocate_lock()
    self.showLog = showLog
    
  def listen(self, host, port):
    self.host = host
    self.port = port
    self.server.bind((self.host, self.port))
    self.server.listen()
    self.__log(f"Socket is listening at {HOST}:{PORT}")
    
    self.__loop()
    
  def __loop(self):
    while True:
      session, address = self.server.accept()
      _thread.start_new_thread(self.__thread, (session, address))
      self.threadCount += 1
      self.__log("Thread Number: " + str(self.threadCount))
      
  def __thread(self, session, address):
    (ip, port) = address
    
    self.__log(f"\nConnection from {ip}:{port} is established")

    payload = session.recv(1024)
    request = HTTPRequest(payload)
    
    print("method", request.method)
    print("path", request.path)
    print("type", request.type)
    
    if request.method == "GET":
      if request.path == "/":
        path = "/index.html"
      else:
        path = request.path
        
      path = f"{self.PUBLIC_DIR}{path}"
      
      if not FileService.exists(path):
        self.error404(session)
      else:
        if request.type == "jpg":
          self.serveJPG(session, path)
        else:
          self.serveHTML(session, path)
    else:
      self.error405(session)

  def error405(self, session):
    response = HTTPResponse(405, "405 Method Not Allowed", "text/html")
    session.send(bytes(response))
    session.close()
      
  def error404(self, session):
    response = HTTPResponse(404, "404 Not Found", "text/html")
    session.send(bytes(response))
    session.close()
        
  def serveHTML(self, session, path):
    content = FileService.readFile(path)
    response = HTTPResponse(200, content, "text/html")
    session.send(bytes(response))
    session.close()
    
  def serveJPG(self, session, path):
    content = FileService.readImageAsBinary(path)
    response = b"HTTP/1.1 200 OK\nContent-Type: image/jpeg\n\n" + content
    session.send(response)
    session.close()
        
  def __log(self, message):
    if self.showLog:
      print(message)


server = TCPServer(showLog=True)
server.listen(HOST, PORT)