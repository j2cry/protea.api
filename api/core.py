import re
import json
from functools import wraps
from sqlalchemy import text
from collections import defaultdict
from flask import make_response, request, jsonify
from flasgger import swag_from

from . import config, app, limiter, db, HOMEPATH
from .service import APIPoint, PagingResult, _parse_query_args, _convert_types, BadRequest, InvalidScopes, InternalError


LIMITS = {}
PAGINATION = defaultdict(dict)

# --------------------------------------------------
# routing
def _get_limits():
    """ Return limit rules for the current endpoint """
    return LIMITS.get(request.endpoint)


def check_token_rights(point):
    def _decorator(func):
        @wraps(func)
        def _wrapper(**kwargs):
            # validate token
            if (token := request.headers.get('token')) is None:
                raise BadRequest('Token is missing')
            # check scopes
            with db[point.storage].engine.connect() as cursor:
                fetched = cursor.execute(text(db[point.storage].scopes_query), parameters={'token': token}).all()
                scopes = set(row[0] for row in fetched)
            if not scopes or not scopes.issuperset(point.scopes.split(',')):
                raise InvalidScopes('Scope is not available for token or token is invalid')
            response = func(**kwargs)
            # after call
            ...
            return response
        return _wrapper
    return _decorator


def _api_callable(point: APIPoint):
    """ API endpoint function builder """
    @check_token_rights(point)
    def _api_endpoint_function(**kwargs):
        token = request.headers['token']
        _query = point.query.strip()
        variables = set(re.findall(r'(?<!:):(\w+)', _query))
        # collect parameters from request body
        try:
            _body = request.json
        except:
            _body = {}
        # collect parameters from query string
        _args = _parse_query_args(request.args)
        # combine all given parameters and convert types
        params = _convert_types({**point.defaults, **_args, **_body, **kwargs, 'token': token},
                                defaults=point.defaults,
                                array_to_string=db[point.storage].array_to_string)
        # check if all required parameters are set
        if vardiff := variables.difference(params.keys()):
            raise BadRequest(f'The necessary parameters are missing: {", ".join(vardiff)}')

        # run query
        try:
            # try to get existing cursor result or receive the new one
            try:
                assert 'nextRows' in params
                paging = PAGINATION[token][point.endpoint]
            except:
                with db[point.storage].engine.connect() as cursor:
                    paging = PagingResult(cursor.execute(text(_query), parameters=params))
            # fetch the next page
            fetched = paging.getnext(params.get('nextRows', paging.rows_count))
        except Exception as ex:
            raise InternalError(str(ex))

        # build response body
        _response = {
            'data': [dict(row._mapping) for row in fetched],
            'paging': {
                'rows_count': paging.rows_count,
                'rows_left': paging.rows_left
            }
        }
        # handle cursor result
        if paging.exhausted:
            PAGINATION[token].pop(point.endpoint, None)
        else:
            PAGINATION[token][point.endpoint] = paging

        return make_response(jsonify(_response), 200)
    return _api_endpoint_function


for section in config.sections():
    if not section.startswith('ENDPOINT:'):
        continue
    # build API method
    try:
        point = APIPoint(
            endpoint=section[section.find(':') + 1:],
            rule=config.get(section, 'rule'),
            method=config.get(section, 'method'),
            scopes=config.get(section, 'scopes', fallback=''),
            query=config.get(section, 'query'),
            storage=config.get(section, 'storage'),
            defaults=config.collect(section, 'default')
        )
    except Exception as ex:
        # log and skip broken point
        print(ex)
        continue
    LIMITS[point.endpoint] = config.get(section, 'limit')
    # register API method
    docfile = config.get(section, 'docfile', fallback=None)
    _documented = swag_from(docfile, endpoint=point.endpoint)(_api_callable(point))
    _limited = limiter.limit(_get_limits)(_documented)
    app.add_url_rule(HOMEPATH.joinpath(point.rule).as_posix(), endpoint=point.endpoint, view_func=_limited, methods=(point.method,))


# --------------------------------------------------
# error handling
@app.errorhandler(Exception)
def hanlde_exception(ex):
    """ Handle API exceptions """
    return make_response({'error': str(ex)}, getattr(ex, 'code', 500))
