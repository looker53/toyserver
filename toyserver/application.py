# -----------------------------------------------
# Author: yuz
# Copyright: 柠檬班
# Email: wagyu2016@163.com
# Phone&Wechat: 18173179913
# -----------------------------------------------
import re
import typing
from collections import namedtuple, defaultdict

from functools import partial

from toyserver.response import Response


class URLMap(typing.NamedTuple):
    url: str
    view_func: typing.Callable
    methods: str


class Router:
    def __init__(self):
        self.url_map = defaultdict()

    def add_map(self, url: str, view_func, name='', methods=None):
        assert url.startswith('/')

        if name in self.url_map.keys():
            raise ValueError(f'route name {name} already exists')

        _, *segments = url.split('/')
        url_pattern = ''
        for segment in segments:
            if segment.startswith('<') and segment.endswith('>'):
                segment_name = segment[1:-1]
                url_pattern += f"/(?P<{segment_name}>[^/]+)"
            else:
                url_pattern += f'/{segment}'

        route_re = re.compile(f'^{url_pattern}$')
        name = name or view_func.__name__
        methods = methods or 'get'
        url_map = URLMap(url=route_re, view_func=view_func, methods=methods)
        self.url_map[name] = url_map

    def lookup(self, url, method):
        for url_map in self.url_map.values():
            match = url_map.url.match(url)
            if match is None or method not in url_map.methods:
                return
            params = match.groupdict()
            return partial(url_map.view_func, **params)


class App:
    def __init__(self, prefix=''):
        self.router = Router()
        self.prefix = prefix

    def add_route(self, url, view_func, name='', methods=None):
        self.router.add_map(self.prefix + url, view_func, name, methods)

    def __call__(self, request):
        view_func = self.router.lookup(request.path, request.method)
        if view_func is None:
            return Response(status='404 Not Found', content='页面不存在')
        return view_func(request)

    def route(self, url, name='', methods=None):
        def decorator(view_func):
            self.add_route(url, view_func, name, methods)
            return view_func
        return decorator


if __name__ == '__main__':
    route = Router()
    route.add_map('/hello/<id>/<group>', lambda x: 'world')
    looked = route.lookup('/hello/3/yuz', 'get')
    print(looked)