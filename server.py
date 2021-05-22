# -----------------------------------------------
# Author: yuz
# Email: wagyu2016@163.com
# Phone&Wechat: 18173179913
# -----------------------------------------------
import socket
from toyserver.request import Request
from toyserver.response import send_file, BAD_REQUEST_RESPONSE
from toyserver.exceptions import BadRequestException

HOST = '127.0.0.1'
PORT = 9000

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

            try:
                # content-length may be not an int string
                content_length = int(request.headers.get('content-length', '0'))
            except ValueError:
                content_length = 0

            body = request.body.read(content_length)
            print('Body is', body)
            send_file(conn, request.path)
        except BadRequestException:
            conn.sendall(BAD_REQUEST_RESPONSE)
