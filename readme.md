# Protea.API

## Configuration
The configuration files are all files with the extension .conf in the conf.d folder, not including the contents of child folders.
The order of reading files is not defined.
<br>
Files cannot contain the same section names except DEFAULT. The DEFAULT section parameters apply to all settings, not just to the file in which they are located.


### Server setup
Global server settings are originally set in file `conf.d/default.conf`

```ini
[SERVER]
host = localhost            # server bind host
port = 23001                # server bind port
homepath = /                # API home path
docspath = /apidocs/        # Swagger docs path
secret_key_length = 40      # secret key length (used to protect cookies)
limits = []                 # default server limits; don't set a very low limit, because it will affect the docs opening
limiter_storage = memory:// # Limiter storage backend, read more: https://flask-limiter.readthedocs.io/en/stable/
```


### Database connections
Connection settings are set in the section `[CONNECTION:{connection_name}]`.
If a password is required to connect to the database, it is recommended to specify it in the environment variable `PROTEA__{connection_name}_PASSWORD`.
In this case, the placeholder `{password}` must be specified in the connection parameters as password.<br>
It is acceptable to specify the password directly, but the special characters must be replaced using the `%xx` escape.
Please note that storing the password in this way is not secure.

Connection parameters can be specified in one of two ways:
```ini
# as connection string
[CONNECTION:{connection_name}]
connection = mssql+pyodbc://sa:{password}@localhost:1433/master?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes
```
or
```ini
# separately
[CONNECTION:{connection_name}]
drivername = mssql+pyodbc
username = sa
password = {password}
host = localhost
port = 1433
database = master
query = {'driver': 'ODBC Driver 18 for SQL Server', 'TrustServerCertificate': 'yes'}
get_scopes_query = ...
array_to_string = true
page_size = 100
```

_get_scopes_query_ - query for receiving token scopes (1 scope per row). If your architecture does not provide access scopes for tokens, you can return any value that is not equivalent to NULL.

_array_to_string_ - experimental parameter for Postgres extended support. Set false to transfer arrays to the database connector without conversion (if your database supports such data types).

_page_size_ - default page size for pagination (__NOT IMPLEMENTED__)


### API endpoint configuration

```ini
[ENDPOINT:{endpoint_name}]
storage = {connection_name} # required; the connection used to execute query
rule = api/method           # required; API method URL
method = GET                # required; acceptable endpoint HTTP-method
limit = 2 per minute        # API method limit
scopes = ...                # token scopes required for this endpoint. Don't set if your architecture does not provide access scopes for tokens
query = SELECT :variable    # query for receiving data
default.{variable}          # default value for variables in the query
docfile = docs/method.yaml  # path to the method docs
```
