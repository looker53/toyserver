# -----------------------------------------------
# Author: yuz
# Email: wagyu2016@163.com
# Phone&Wechat: 18173179913
# -----------------------------------------------

from toyserver.server import HTTPServer
from toyserver.response import Response
from toyserver.middleware import jwt

server = HTTPServer()


@server.route('/')
@jwt
def index(request):
    return Response('Hello World')


@server.route('/login')
def login(request):
    return Response('Login Page')


# or use add_router to resister url
# server.add_router('/', index)
# server.add_router('/login', login)

server.listen()
