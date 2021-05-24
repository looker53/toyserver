# -----------------------------------------------
# Author: yuz
# Email: wagyu2016@163.com
# Phone&Wechat: 18173179913
# -----------------------------------------------
from toyserver.response import Response


def jwt(handler):

    def login(request):
        token = request.headers.get('Authorization', '')
        token_type, _, token = token.partition(' ')
        if token:
            return handler(request)
        return Response('please add a token', status='403 Forbidden')

    return login
