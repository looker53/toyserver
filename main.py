# -----------------------------------------------
# Author: yuz
# Email: wagyu2016@163.com
# Phone&Wechat: 18173179913
# -----------------------------------------------
from toyserver.application import App
from toyserver.server import HTTPServer
from toyserver.response import Response
from toyserver.middleware import jwt

server = HTTPServer(port=9000)
app = App()
server.mount('', app)


@app.route('/')
def index(request):
    return Response('Hello World')


@app.route('/login')
def login(request):
    return Response('Login Page')

print(app.router)
# or use add_router to resister url
# server.add_router('/', index)
# server.add_router('/login', login)

server.listen()
