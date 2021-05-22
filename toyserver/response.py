# -----------------------------------------------
# Author: yuz
# Copyright: 柠檬班
# Email: wagyu2016@163.com
# Phone&Wechat: 18173179913
# -----------------------------------------------
import socket
import pathlib
import mimetypes

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
            sock.sendall(NOT_FOUND_RESPONSE)
            return
    except OSError:
        sock.sendall(BAD_REQUEST_RESPONSE)
        return

    content_type, encoding = mimetypes.guess_type(file_path)
    if content_type is None:
        content_type = 'application/octet-stream'
    if encoding is not None:
        content_type += f'; charset={encoding}'
    size = file_path.stat().st_size
    headers = FILE_RESPONSE_TEMPLATE.format(content_type=content_type,
                                            content_length=size)
    sock.sendall(headers.encode('utf-8'))
    with file_path.open('rb', encoding=encoding) as f:
        sock.sendfile(f)
