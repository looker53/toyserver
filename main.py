# -----------------------------------------------
# Author: yuz
# Email: wagyu2016@163.com
# Phone&Wechat: 18173179913
# -----------------------------------------------
from toyserver.application import App
from toyserver.server import HTTPServer
from toyserver.response import Response, JsonResponse
from toyserver.middleware import jwt

server = HTTPServer(port=9000)
app = App()
server.mount('', app)


@app.route('/')
def index(request):
    # return Response('{"msg": "OK", "data": "..."}', headers={'content-type': 'application/json'})
    return JsonResponse({"msg": "ok", "data": "你好"})


@app.route('/login')
def login(request):
    return Response('Login Page')


@app.route('/user/<id>', methods=['POST'])
def user(request, id):
    print(request.json)
    return Response('User Page')

print(app.router)
# or use add_router to resister url
# server.add_router('/', index)
# server.add_router('/login', login)

server.listen()
