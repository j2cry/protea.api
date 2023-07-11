from api import app, HOST, PORT
from gevent.pywsgi import WSGIServer


if __name__ == '__main__':
    server = WSGIServer((HOST, PORT), app, environ={'wsgi.multithread': True})
    server.serve_forever()
