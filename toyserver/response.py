# -----------------------------------------------
# Author: yuz
# Copyright: 柠檬班
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

# 每行用 \r\n 分割，content-length 长度确认
RESPONSE = b"""\
HTTP/1.1 200 OK
Content-type: text/html
Content-length: 18

<h1>Hello Yuz!</h1>""".replace(b'\n', b'\r\n')

# 静态文件请求模板
FILE_RESPONSE_TEMPLATE = """\
HTTP/1.1 200 OK
Content-type: {content_type}
Content-length: {content_length}

""".replace('\n', '\r\n')

# bad request 响应结果
BAD_REQUEST_RESPONSE = b"""\
HTTP/1.1 400 Bad Request
Content-type: text/plain
Content-length: 11

Bad Request""".replace(b"\n", b"\r\n")

# not found 响应结果
NOT_FOUND_RESPONSE = b"""\
HTTP/1.1 404 Not Found
Content-type: text/plain
Content-length: 9

Not Found""".replace(b"\n", b"\r\n")


def send_file(sock: socket.socket, path: str) -> None:
    """发送静态文件给客户端"""
    if path == '/':
        path = '/index.html'

    relative_file_path = pathlib.Path(STATIC_PATH) / path.lstrip('/')
    file_path = relative_file_path.resolve()
    try:
        if not file_path.exists():
            # sock.sendall(NOT_FOUND_RESPONSE)
            # return
            response = Response('page missing', status='404 Not Found')
            return response.send(sock)
    except OSError:
        # sock.sendall(BAD_REQUEST_RESPONSE)
        # return
        response = Response('page missing', status='404 Not Found')
        return response.send(sock)

    content_type, encoding = mimetypes.guess_type(file_path)
    if content_type is None:
        content_type = 'application/octet-stream'
    if encoding is not None:
        content_type += f'; charset={encoding}'
    # size = file_path.stat().st_size
    # headers = FILE_RESPONSE_TEMPLATE.format(content_type=content_type,
    #                                         content_length=size)
    # sock.sendall(headers.encode('utf-8'))
    # with file_path.open('rb', encoding=encoding) as f:
    #     sock.sendfile(f)

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
