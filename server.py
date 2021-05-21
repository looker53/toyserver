# -----------------------------------------------
# Author: yuz
# Email: wagyu2016@163.com
# Phone&Wechat: 18173179913
# -----------------------------------------------
import socket

HOST = '127.0.0.1'
PORT = 9000

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
            conn.sendall(RESPONSE)
