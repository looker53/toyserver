# -----------------------------------------------
# Author: yuz
# Email: wagyu2016@163.com
# Phone&Wechat: 18173179913
# -----------------------------------------------
import socket
from .request import Request
from .response import send_file, Response
from .exceptions import BadRequestException


class HTTPServer:
    def __init__(
            self,
            host=None,
            port: int = None,
    ):
        self.host = host or '127.0.0.1'
        self.port = port or 9001

    def listen(self):
        with socket.socket() as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((self.host, self.port))
            # 0怎么确定的? 学习 socket 协议簇
            sock.listen(0)
            print(f"listen on http://{self.host}:{self.port}")
            while True:
                conn, address = sock.accept()
                self.handle_request(conn, address)

    @staticmethod
    def handle_request(client_sock: socket.socket, client_address):
        with client_sock:
            try:
                request = Request.from_socket(client_sock)
                try:
                    # content-length may be not an int string
                    content_length = int(request.headers.get('content-length', '0'))
                except ValueError:
                    content_length = 0

                body = request.body.read(content_length)
                send_file(client_sock, request.path)
            except BadRequestException:
                # conn.sendall(BAD_REQUEST_RESPONSE)
                response = Response('you send a bad request', status='400 Bad Request')
                response.send(client_sock)
