# -----------------------------------------------
# Author: yuz
# Email: wagyu2016@163.com
# Phone&Wechat: 18173179913
# -----------------------------------------------
import socket
import typing

HOST = '127.0.0.1'
PORT = 9000
# 每行用 \r\n 分割，content-length 长度确认
RESPONSE = b"""\
HTTP/1.1 200 OK
Content-type: text/html
Content-length: 18

<h1>Hello Yuz!</h1>""".replace(b'\n', b'\r\n')

# bad request 响应结果
BAD_REQUEST_RESPONSE = b"""\
HTTP/1.1 400 Bad Request
Content-type: text/plain
Content-length: 11

Bad Request""".replace(b"\n", b"\r\n")

# not foound 响应结果
NOT_FOUND_RESPONSE = b"""\
HTTP/1.1 404 Not Found
Content-type: text/plain
Content-length: 9

Not Found""".replace(b"\n", b"\r\n")


class BadRequestException(Exception):
    pass


class Request(typing.NamedTuple):
    """请求类"""
    path: str
    method: str
    headers: typing.Mapping

    @classmethod
    def from_socket(cls, sock: socket.socket) -> 'Request':
        lines = iter_request_lines(sock)
        try:
            request_line = next(lines).decode()
        except StopIteration:
            raise BadRequestException('no request line')

        method, path, _ = request_line.split(' ')

        headers = {}
        for line in lines:
            key, _, value = line.decode().partition(':')
            headers[key.lower()] = value.lstrip()
        return cls(path=path, method=method, headers=headers)


def iter_request_lines(sock: socket.socket, buff_size=1024):
    """获取请求的每行数据"""
    buff: bytes = b''
    while True:
        data = sock.recv(buff_size)
        if not data:
            return b''

        buff += data
        while True:
            try:
                line, buff = buff.split(b'\r\n', maxsplit=1)
                yield line
            except ValueError:
                return buff


with socket.socket() as sock:
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, PORT))
    # 0怎么确定的? 学习 socket 协议簇
    sock.listen(0)
    print(f"listen on {HOST}:{PORT}")
    while True:
        conn, address = sock.accept()
        print(f"new connection from {address}")
        try:
            request = Request.from_socket(conn)
            print(f"请求数据:{request}")
            conn.sendall(NOT_FOUND_RESPONSE)
        except BadRequestException:
            conn.sendall(BAD_REQUEST_RESPONSE)
