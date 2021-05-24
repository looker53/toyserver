# -----------------------------------------------
# Author: yuz
# Email: wagyu2016@163.com
# Phone&Wechat: 18173179913
# -----------------------------------------------

from toyserver.server import HTTPServer
from toyserver.response import Response


def index(request):
    return Response('Hello World')


def login(request):
    return Response('Login Page')


server = HTTPServer()
server.add_router('/', index)
server.add_router('/login', login)

server.listen()
