# -----------------------------------------------
# Author: yuz
# Email: wagyu2016@163.com
# Phone&Wechat: 18173179913
# -----------------------------------------------
import socket
import pathlib
import mimetypes
import typing
import os
from io import BytesIO

STATIC_PATH = pathlib.Path(__file__).parent.parent / 'static'


def send_file(sock: socket.socket, path: str) -> None:
    """发送静态文件给客户端"""
    if path == '/':
        path = '/index.html'

    relative_file_path = pathlib.Path(STATIC_PATH) / path.lstrip('/')
    file_path = relative_file_path.resolve()
    try:
        if not file_path.exists():
            response = Response('page missing', status='404 Not Found')
            return response.send(sock)
    except OSError:
        response = Response('page missing', status='404 Not Found')
        return response.send(sock)

    content_type, encoding = mimetypes.guess_type(file_path)
    if content_type is None:
        content_type = 'application/octet-stream'
    if encoding is not None:
        content_type += f'; charset={encoding}'

    with file_path.open('rb', encoding=encoding) as f:
        response = Response(body=f, status='200 OK')
        response.headers['content-type'] = content_type
        return response.send(sock)


class Response:
    def __init__(
            self,
            content: str = None,
            body: typing.Optional[typing.IO] = None,
            headers: typing.Mapping[str, str] = None,
            status: str = None,
            encoding='utf-8'
    ):
        if content:
            # 像文件一样可以读取的文本流
            self.body = BytesIO(content.encode(encoding))
        elif body:
            self.body = body
        else:
            self.body = BytesIO()

        self.headers = headers or {}
        self.status = status.encode() or b'200 OK'

    def send(self, sock: socket.socket):
        content_length = self.headers.get('content-length')
        if content_length is None:
            try:
                body_stat = os.fstat(self.body.fileno())
                content_length = body_stat.st_size
            except OSError:
                self.body.seek(0, os.SEEK_END)
                content_length = self.body.tell()
                self.body.seek(0, os.SEEK_SET)
            self.headers.setdefault('content-length', content_length)

        request_line = b'HTTP/1.1 ' + self.status + b'\r\n'
        for header_name, header_value in self.headers.items():
            request_line += f'{header_name}: {header_value}\r\n'.encode()
        request_line += b'\r\n'

        sock.sendall(request_line)
        if content_length > 0:
            sock.sendfile(self.body)
        print(f'<-- {self.status}')
