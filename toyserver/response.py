# -----------------------------------------------
# Author: yuz
# Email: wagyu2016@163.com
# Phone&Wechat: 18173179913
# -----------------------------------------------
import socket
import pathlib
import mimetypes
import typing
import json
import os
from io import BytesIO

from toyserver.request import Request


def send_static_file(static_folder: str):
    def static_router(request: Request) -> Response:
        """发送静态文件给客户端"""
        _, _, static_url_without_prefix = request.path.lstrip('/').partition('/')
        static_file_path = pathlib.Path(static_folder) / static_url_without_prefix.lstrip('/')
        file_path = static_file_path.resolve()
        try:
            if not file_path.exists():
                return Response('page missing', status='404 Not Found')
        except OSError:
            return Response('page missing', status='404 Not Found')

        content_type, encoding = mimetypes.guess_type(file_path)
        if content_type is None:
            content_type = 'application/octet-stream'
        if encoding is not None:
            content_type += f'; charset={encoding}'

        f = file_path.open('rb', encoding=encoding)
        response = Response(body=f, status='200 OK')
        response.headers['content-type'] = content_type
        return response
    return static_router


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
        status = status or '200 OK'
        self.status = status.encode()
        self.encoding = encoding

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
            content_type = self.headers.get('content-type', 'text/html')
            content_type += f';charset={self.encoding}'
            self.headers['content-type'] = content_type

        request_line = b'HTTP/1.1 ' + self.status + b'\r\n'
        for header_name, header_value in self.headers.items():
            request_line += f'{header_name}: {header_value}\r\n'.encode()
        request_line += b'\r\n'

        sock.sendall(request_line)
        if content_length > 0:
            sock.sendfile(self.body)
        print(f'<-- {self.status}')


class JsonResponse(Response):
    def __init__(
            self,
            content,
            body=None,
            headers: typing.Mapping[str, str] = None,
            status: str = None,
            encoding='utf-8'
    ):
        content = json.dumps(content)
        super().__init__(content,
                         body,
                         headers,
                         status,
                         encoding)
        self.headers['content-type'] = 'application/json'

