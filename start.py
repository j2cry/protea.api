import eventlet
from eventlet import wsgi
from api import app, HOST, PORT


if __name__ == '__main__':
    wsgi.server(eventlet.listen((HOST, PORT)), app)
