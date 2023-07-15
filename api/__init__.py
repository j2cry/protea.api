import os
import pathlib
from ast import literal_eval
from sqlalchemy import URL, create_engine
from urllib.parse import quote

from flask import Flask, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flasgger import Swagger

from .defaults import Default
from .service import CustomConfigParser, CustomJSONProvider, StorageDesc


# --------------------------------------------------
# read configuration
assert os.path.exists(Default.CONFIG_FOLDER), 'Configuration path not exists! Installation is broken.'
config = CustomConfigParser(converters={'eval': literal_eval})
config.read(os.path.join(Default.CONFIG_FOLDER, f) for f in os.listdir(Default.CONFIG_FOLDER) if f.endswith('.conf'))

# --------------------------------------------------
# init database connections
db = {}
for section in config.sections():
    if not section.startswith('CONNECTION:'):
        continue
    name = section[11:]
    try:
        _connstr = config.get(section, 'connection')
        if '{password}' in _connstr:
            _connstr = _connstr.replace('{password}', quote(str(os.environ.get(f'PROTEA__{name.upper()}_PASSWORD'))))
    except:
        _connstr = URL.create(
            drivername=config.get(section, 'drivername'),
            username=config.get(section, 'username', fallback=None),
            password=config.get(section, 'password', fallback=None),
            host=config.get(section, 'host', fallback=None),
            port=config.get(section, 'port', fallback=None),
            database=config.get(section, 'database', fallback=None),
            query=config.geteval(section, 'query', fallback={})
        )
    get_scopes_query = config.get(section, 'get_scopes_query').strip()
    array_to_string = config.getboolean(section, 'array_to_string', fallback=Default.ARRAY_TO_STRING)
    db[name] = StorageDesc(create_engine(_connstr), get_scopes_query, array_to_string)
    # check connection
    with db[name].engine.connect() as cursor:
        pass
del _connstr

# --------------------------------------------------
# collect server parameters
HOST = config.get('SERVER', 'host', fallback=Default.HOST)
PORT = config.getint('SERVER', 'port', fallback=Default.PORT)
HOMEPATH = pathlib.Path('/', config.get('SERVER', 'homepath'))

# --------------------------------------------------
# init application
SECRET_KEY_LENGTH = config.getint('SERVER', 'secret_key_length')
app = Flask(__name__, static_folder=None, static_url_path=HOMEPATH.joinpath('static').as_posix())
app.config['SECRET_KEY'] = os.urandom(SECRET_KEY_LENGTH).hex()
app.json = CustomJSONProvider(app)

# --------------------------------------------------
# init limiter
limiter = Limiter(
    lambda: request.headers.get('token', get_remote_address()),   # NOTE if None Limiter doesn't affect
    app=app,
    default_limits=config.geteval('SERVER', 'limits', fallback=Default.LIMITS),
    storage_uri=config.get('SERVER', 'limiter_storage', fallback=Default.LIMITER_STORAGE),
    headers_enabled=True
)

# --------------------------------------------------
# init Swagger
swagger_config = {
    'title': 'Protea.API',
    'specs': [{
        'endpoint': f'protea-api',
        'route': f'/protea-api.json',
        'rule_filter': lambda rule: True,
        'model_filter': lambda tag: True,
    }],
    # "static_url_path": "/static",
    'specs_route': pathlib.Path('/', config.get('SERVER', 'docspath')).as_posix() + '/',
    # "url_prefix": "/"
}
swagger = Swagger(app, config=swagger_config, template_file='docs/default.yaml', merge=True)


import api.core
