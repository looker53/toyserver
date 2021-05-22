# -----------------------------------------------
# Author: yuz
# Email: wagyu2016@163.com
# Phone&Wechat: 18173179913
# -----------------------------------------------
import socket
from queue import Queue, Empty
from threading import Thread

from .request import Request
from .response import send_file, Response
from .exceptions import BadRequestException


class HTTPWorker(Thread):
    def __init__(self, connection_queue: Queue):
        super().__init__(daemon=True)
        self.connection_queue = connection_queue
        self.running = False

    def stop(self):
        self.running = False

    def run(self):
        self.running = True
        while self.running:
            try:
                client_sock, client_address = self.connection_queue.get(timeout=1)
            except Empty:
                continue
            try:
                self.handle_client(client_sock, client_address)
            except:
                print("不能处理的请求")
                continue
            finally:
                self.connection_queue.task_done()

    def handle_client(self, client_sock: socket.socket, client_address):
        with client_sock:
            try:
                request = Request.from_socket(client_sock)
                print(f'--> {request.method} {request.path} from {client_address} ')
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


class HTTPServer:
    def __init__(
            self,
            host=None,
            port: int = None,
            workers = 16
    ):
        self.host = host or '127.0.0.1'
        self.port = port or 9001
        self.worker_count = workers
        self.worker_backlog = self.worker_count * 8
        self.connection_queue = Queue(maxsize=self.worker_backlog)

    def listen(self):
        workers = []
        for _ in range(self.worker_count):
            worker = HTTPWorker(self.connection_queue)
            worker.start()
            workers.append(worker)

        with socket.socket() as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((self.host, self.port))
            # 0怎么确定的? 学习 socket 协议簇
            sock.listen(self.worker_backlog)
            print(f"listen on http://{self.host}:{self.port}")
            while True:
                try:
                    self.connection_queue.put(sock.accept())
                except KeyboardInterrupt:
                    break

        [worker.stop() for worker in workers]
        [worker.join(timeout=30) for worker in workers]

    # @staticmethod
    # def handle_request(client_sock: socket.socket, client_address):
    #     with client_sock:
    #         try:
    #             request = Request.from_socket(client_sock)
    #             try:
    #                 # content-length may be not an int string
    #                 content_length = int(request.headers.get('content-length', '0'))
    #             except ValueError:
    #                 content_length = 0
    #
    #             body = request.body.read(content_length)
    #             send_file(client_sock, request.path)
    #         except BadRequestException:
    #             # conn.sendall(BAD_REQUEST_RESPONSE)
    #             response = Response('you send a bad request', status='400 Bad Request')
    #             response.send(client_sock)
