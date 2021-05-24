# -----------------------------------------------
# Author: yuz
# Email: wagyu2016@163.com
# Phone&Wechat: 18173179913
# -----------------------------------------------
import socket
import typing
from .exceptions import BadRequestException


class Body:
    """请求体读取。"""
    def __init__(self, sock: socket.socket, buff=b'', buff_size=1024):
        self._sock = sock
        self._buff = buff
        self._buff_size = buff_size

    def read(self, n):
        while len(self._buff) < n:
            data = self._sock.recv(self._buff_size)
            if not data:
                break

            self._buff += data
        res, self._buff = self._buff[:n], self._buff[n:]
        return res


class Request(typing.NamedTuple):
    """请求类"""
    path: str
    method: str
    headers: typing.Mapping
    body: Body
    args: str

    @classmethod
    def from_socket(cls, sock: socket.socket) -> 'Request':
        lines = iter_request_lines(sock)
        try:
            request_line = next(lines).decode()
        except StopIteration:
            raise BadRequestException('no request line')

        method, path, _ = request_line.split(' ')
        path, _, args = path.partition('?')
        headers = {}
        while True:
            try:
                line = next(lines)
            except StopIteration as e:
                # StopIteration 得到 lines 生成器的返回值
                buff = e.value
                break

            key, _, value = line.decode().partition(':')
            headers[key.lower()] = value.lstrip()

        body = Body(sock, buff=buff)
        return cls(path=path, method=method, headers=headers, body=body, args=args)


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