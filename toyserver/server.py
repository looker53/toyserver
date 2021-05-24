# -----------------------------------------------
# Author: yuz
# Email: wagyu2016@163.com
# Phone&Wechat: 18173179913
# -----------------------------------------------
import socket
from queue import Queue, Empty
from threading import Thread

from .request import Request
from .response import Response, send_static_file


STATIC_URL = '/static'
STATIC_FOLDER = 'static'


class HTTPWorker(Thread):
    def __init__(self, connection_queue: Queue, routers):
        super().__init__(daemon=True)
        self.connection_queue = connection_queue
        self.routers = routers
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
            except Exception:
                # conn.sendall(BAD_REQUEST_RESPONSE)
                response = Response('you send a bad request', status='400 Bad Request')
                response.send(client_sock)
                return

            for url, handler in self.routers:
                if request.path == '/' == url:
                    response = handler(request)
                    response.send(client_sock)
                    return

                if request.path.startswith(url):
                    try:
                        response = handler(request)
                        response.send(client_sock)
                    except Exception as e:
                        response = Response('Server Error', status='500 Internal Server Error')
                        response.send(client_sock)
                    finally:
                        break
            else:
                response = Response('Page not found', status='404 Not Found')
                response.send(client_sock)
                return


class HTTPServer:
    def __init__(
            self,
            host=None,
            port: int = None,
            workers=16
    ):
        self.host = host or '127.0.0.1'
        self.port = port or 9001
        self.worker_count = workers
        self.worker_backlog = self.worker_count * 8
        self.connection_queue = Queue(maxsize=self.worker_backlog)
        self.routers = []
        # self.static_folder = 'static'
        # self.static_url = 'static'

        self.add_router(STATIC_URL, send_static_file(STATIC_FOLDER))

    def listen(self):
        workers = []
        for _ in range(self.worker_count):
            worker = HTTPWorker(self.connection_queue, self.routers)
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

    def add_router(self, url, handler):
        self.routers.append((url, handler))
