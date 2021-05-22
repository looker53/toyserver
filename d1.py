# -----------------------------------------------
# Author: yuz
# Email: wagyu2016@163.com
# Phone&Wechat: 18173179913
# -----------------------------------------------

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
