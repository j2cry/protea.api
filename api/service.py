import json
import datetime as dt
from ast import literal_eval
from configparser import RawConfigParser, NoSectionError, NoOptionError, _UNSET
from decimal import Decimal
from collections import namedtuple
from flask.json.provider import JSONProvider
from sqlalchemy import CursorResult

from .defaults import Default

# --------------------------------------------------
class CustomConfigParser(RawConfigParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.optionxform = lambda v: v

    def get(self, section: str, option: str, *, raw=False, vars=None, fallback=_UNSET):
        try:
            value = super().get(section, option, raw=raw, vars=vars, fallback=fallback)
        except (NoSectionError, NoOptionError):
            value = getattr(Default, option.upper(), _UNSET)
            if value is _UNSET:
                # stderr = f'Parameter `[{section}] {option}` is not set and has no default value.'
                raise NoOptionError(option, section)
        return value

    def collect(self, section, tags, convert=True):
        _result = {}
        _tags = tags.split('.') if isinstance(tags, str) else tags
        for key, value in self[section].items():
            _parsed = set(key.split('.'))
            if _parsed.issuperset(_tags) and len(tag := _parsed.difference(_tags)) == 1:
                try:
                    _result[tag.pop()] = literal_eval(value) if convert else value
                except:
                    _result[tag.pop()] = value
        return _result

# --------------------------------------------------
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, dt.datetime):
            return obj.isoformat()
        else:
            return obj
        return JSONEncoder.default(self, obj)

class CustomJSONProvider(JSONProvider):
    def dumps(self, obj, **kwargs):
        return json.dumps(obj, **kwargs, cls=CustomJSONEncoder)

    def loads(self, s: str | bytes, **kwargs):
        return json.loads(s, **kwargs)

# --------------------------------------------------
APIPoint = namedtuple('APIPoint', 'endpoint,rule,method,scopes,query,storage,defaults')
StorageDesc = namedtuple('StorageDesc', 'engine,scopes_query,array_to_string')

# --------------------------------------------------
class PagingResult:
    def __init__(self, cursor_result: CursorResult):
        self.__cr = cursor_result
        self.rows_count = cursor_result.rowcount
        self.rows_left = cursor_result.rowcount

    def getnext(self, size: int = None):
        self.rows_left = max(0, self.rows_left - size)
        return self.__cr.fetchmany(size)

    @property
    def exhausted(self) -> bool:
        return self.rows_left == 0


# --------------------------------------------------
def _parse_query_args(args):
    _args = {}
    for key, value in args.items(multi=True):
        try:
            value = literal_eval(value)
        except:
            pass
        if key in _args:
            if not isinstance(_args[key], list):
                _args[key] = [_args[key]]
            _args[key].append(value)
        else:
            _args[key] = value
    return _args


def _convert_types(p: dict, defaults: dict, array_to_string: bool):
    """ Convert types to given defaults and cast arrays to str if required """
    params = {}
    for key, value in p.items():
        if (_default := defaults.get(key)) is None:     # no default value
            params[key] = value
            continue
        # change target type: tuple to list
        if (_dtype := type(_default)) is tuple:
            _dtype = list
        # types equal
        if isinstance(value, _dtype):
            params[key] = ','.join(map(str, value)) if isinstance(value, (list, tuple)) and array_to_string else value
            continue
        # types mismatch
        if _dtype is list and not isinstance(value, tuple):
            params[key] = str(value) if array_to_string else [value]
        else:
            try:
                params[key] = ','.join(map(str, value)) if isinstance(value, (list, tuple)) and array_to_string else _dtype(value)
            except:
                raise BadRequest(f'Cannot interpret parameter {key} with value {value} as type {_dtype}')
    return params

# --------------------------------------------------
# Exceptions
class BadRequest(Exception):
    code = 400

class InvalidScopes(Exception):
    code = 401

class InternalError(Exception):
    code = 500
