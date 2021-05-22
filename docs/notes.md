## 生成器的使用

当使用 next() 生成数据时，得到 yield 数据，当迭代完成，报
 StopIteration 错误，可以通过 e.value 获取生成器 return 的返回值。

```python
def gen():
    for i in range(5):
        if i == 4:
            return "hello"
        yield i


g = gen()
while True:
    try:
        i = next(g)
        print("hey", i)
    except StopIteration as e:
        print(e)
```

在服务器处理中，Request 的 from_socket 函数可以处理请求数据,处理请求行是一个生成器，
yield 数据是每一行头信息，剩下的数据是请求体的部分内容，是这个生成器的返回值。
当生成器报 StopIteration， 可以通过 buff 接收请求体的部分数据。
```python
lines = iter_request_lines(sock)
...
headers = {}
while True:
    try:
        line = next(lines)
    except StopIteration as e:
        # StopIteration 得到 lines 生成器的返回值
        buff = e.value
        break
```