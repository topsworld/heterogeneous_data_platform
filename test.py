import tornado.ioloop
import tornado.web
from tornado.web import RequestHandler, Application, url
from tornado import httpclient, gen
import tornado.httpserver, time
class MainHandler(RequestHandler):
    def initialize(self):
        print("helloooooo")
 
    async def get(self):
        http = tornado.httpclient.AsyncHTTPClient()
        await gen.sleep(2)
        self.write("Hello")
def make_app():
    db = "hello"
    app = Application([url(r"/", MainHandler)])
    return app
 
async def loop(name):
    while True:
        print(name)
        await gen.sleep(1)
 
def block(num):
    while True:
        print(num)
        time.sleep(2)
 
if __name__ == '__main__':
    app = make_app()
    app.listen(8000)
    print("开启监听")
    io = tornado.ioloop.IOLoop.current()
    io.run_in_executor(None, block, "run_in_executor")
    io.add_callback(loop, "add_callback")
    io.spawn_callback(loop, "spawn_callback")
    io.start()
    print("end")