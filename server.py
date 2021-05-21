# -----------------------------------------------
# Author: yuz
# Email: wagyu2016@163.com
# Phone&Wechat: 18173179913
# -----------------------------------------------
import socket
import typing

HOST = '127.0.0.1'
PORT = 9000


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


# 每行用 \r\n 分割，content-length 长度确认
RESPONSE = b"""\
HTTP/1.1 200 OK
Content-type: text/html
Content-length: 18

<h1>Hello Yuz!</h1>""".replace(b'\n', b'\r\n')

with socket.socket() as sock:
    sock.bind((HOST, PORT))
    # 0怎么确定的? 学习 socket 协议簇
    sock.listen(0)
    print(f"listen on {HOST}:{PORT}")
    while True:
        conn, address = sock.accept()
        print(f"new connection from {address}")
        with conn:
            for line in iter_request_lines(conn):
                print(line)
            conn.sendall(RESPONSE)
