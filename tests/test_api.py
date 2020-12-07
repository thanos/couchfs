import os

import pytest
import requests_mock
from couchfs.api import CouchDBClient, BadConnectionURI, URLRequired


#
#

#
#


attachment_list = {"total_rows":3,"offset":0,"rows":[
{"id":"1","key":["1"],"value":0},
{"id":"doc-1","key":["doc-1","isis28.gif"],"value":10415},
{"id":"doc-2","key":["doc-2"],"value":0}
]}



def test_connection_str():
    scheme = 'http'
    username = 'username'
    password = 'password'
    host = 'host'
    port = '5984'
    database = 'database'
    connection_str = f'couchdb://{username}:{password}@{host}:{port}/{database}'
    db_uri = f'http://{host}:{port}/{database}'
    client = CouchDBClient(connection_str)
    assert client.db == database
    assert client.db_uri == db_uri
    assert client.auth == (username, password)

def test_connection_str_couchdbs():
    scheme = 'http'
    username = 'username'
    password = 'password'
    host = 'host'
    port = '5984'
    database = 'database'
    connection_str = f'couchdbs://{username}:{password}@{host}:{port}/{database}'
    db_uri = f'https://{host}:{port}/{database}'
    client = CouchDBClient(connection_str)
    assert client.db_uri == db_uri

def test_connection_str_no_auth():
    scheme = 'http'
    host = 'host'
    port = '5984'
    database = 'database'
    connection_str = f'couchdb://{host}:{port}/{database}'
    db_uri = f'http://{host}:{port}/{database}'
    client = CouchDBClient(connection_str)
    assert client.db_uri == db_uri
    assert client.auth is None


def test_connection_str_no_database():
    scheme = 'http'
    host = 'host'
    port = '5984'
    database = 'database'
    connection_str = f'couchdb://{host}:{port}/'
    db_uri = f'http://{host}:{port}/{database}'
    with pytest.raises(BadConnectionURI):
        CouchDBClient(connection_str)

def test_env_connection_str():
    scheme = 'http'
    host = '127.0.0.1'
    port = '5984'
    database = 'test'
    connection_str = f'couchdb://{host}:{port}/{database}'
    db_uri = f'http://{host}:{port}/{database}'
    os.environ[CouchDBClient.URI_ENVIRON_KEY] = connection_str
    client = CouchDBClient()
    assert client.db_uri == db_uri

def test_no_connection_str():
    class NoConStr(CouchDBClient):
        URI_ENVIRON_KEY = 'XXXX'
    with pytest.raises(URLRequired):
        NoConStr()


def test_list_attchments_one_pattern():
    host = '127.0.0.1'
    port = '5984'
    database = 'test'
    connection_str = f'couchdb://{host}:{port}/{database}'
    params = {'reduce': False, 'include_docs': False}
    with requests_mock.Mocker() as m:
        client = CouchDBClient(connection_str)
        m.get(f'{client.db_uri}/_design/couchfs_views/_view/attachment_list?reduce=false', json={"total_rows":3,"offset":0,"rows":[
{"id":"1","key":["1"],"value":0},
{"id":"doc-1","key":["doc-1","isis28.gif"],"value":10415},
{"id":"doc-2","key":["doc-2"],"value":0}
]})
        assert len(list(client.list_attachments('doc-1'))) == 1

def test_list_attchments_two_patterns():
    host = '127.0.0.1'
    port = '5984'
    database = 'test'
    connection_str = f'couchdb://{host}:{port}/{database}'
    with requests_mock.Mocker() as m:
        client = CouchDBClient(connection_str)
        m.get(f'{client.db_uri}/_design/couchfs_views/_view/attachment_list?reduce=false',
              json={"total_rows": 3, "offset": 0, "rows": [
                  {"id": "1", "key": ["1"], "value": 0},
                  {"id": "doc-1", "key": ["doc-1", "isis28.gif"], "value": 10415},
                  {"id": "doc-2", "key": ["doc-2"], "value": 0}
              ]})
        assert len(list(client.list_attachments('doc-1','doc-2'))) == 2

def test_list_attchments_no_patterns():
    host = '127.0.0.1'
    port = '5984'
    database = 'test'
    connection_str = f'couchdb://{host}:{port}/{database}'
    with requests_mock.Mocker() as m:
        client = CouchDBClient(connection_str)
        m.get(f'{client.db_uri}/_design/couchfs_views/_view/attachment_list?reduce=false',
              json={"total_rows": 3, "offset": 0, "rows": [
                  {"id": "1", "key": ["1"], "value": 0},
                  {"id": "doc-1", "key": ["doc-1", "isis28.gif"], "value": 10415},
                  {"id": "doc-2", "key": ["doc-2"], "value": 0}
              ]})
        assert len(list(client.list_attachments())) == 3


def test_get_attachment():
    host = '127.0.0.1'
    port = '5984'
    database = 'test'
    connection_str = f'couchdb://{host}:{port}/{database}'
    with requests_mock.Mocker() as m:
        client = CouchDBClient(connection_str)
        m.get(f'{client.db_uri}/DOC/wsgi.py', content=bytes('1'*10, 'utf-8'))
        with client.get_attachment(f'{client.db_uri}/DOC/wsgi.py') as fp:
            assert len(fp.read()) == 10
            assert os.path.exists(fp.name)
        assert not os.path.exists(fp.name)



def test_get_attachment_in_memory():
    host = '127.0.0.1'
    port = '5984'
    database = 'test'
    connection_str = f'couchdb://{host}:{port}/{database}'
    with requests_mock.Mocker() as m:
        client = CouchDBClient(connection_str)
        m.get(f'{client.db_uri}/DOC/wsgi.py', content=bytes('1'*10, 'utf-8'))
        with CouchDBClient(connection_str).get_attachment(f'{client.db_uri}/DOC/wsgi.py',in_memory=True) as buff:
            assert len(buff) == 10
        assert len(buff) == 10


def test_upload_file_existing_doc():
    host = '127.0.0.1'
    port = '5984'
    database = 'test'
    connection_str = f'couchdb://{host}:{port}/{database}'
    doc_id = 'DOC'
    headers = {'Cache-Control': 'must-revalidate', 'Content-Length': '55002', 'Content-Type': 'application/json', 'Date': 'Mon, 07 Dec 2020 18:32:24 GMT', 'ETag': '"361-31e194e4bb0c4e4507f6c43428bd9bc3"', 'Server': 'CouchDB/3.1.1 (Erlang OTP/22)', 'X-Couch-Request-ID': 'a27fd9fe9b', 'X-CouchDB-Body-Time': '0'}
    client = CouchDBClient(connection_str)
    with requests_mock.Mocker() as doc_check:
        doc_check.register_uri('HEAD', f'{client.db_uri}/{doc_id}', status_code=200, headers=headers)
        doc_check.register_uri('PUT', f'{client.db_uri}/{doc_id}/test.py', status_code=201)
        with open(__file__, 'rb') as fp:
            client.upload_file(fp, f'{doc_id}/test.py')


def test_upload_file_new_doc():
    host = '127.0.0.1'
    port = '5984'
    database = 'test'
    connection_str = f'couchdb://{host}:{port}/{database}'
    doc_id = 'DOC'
    client = CouchDBClient(connection_str)
    with requests_mock.Mocker() as doc_check:
        doc_check.register_uri('HEAD', f'{client.db_uri}/{doc_id}', status_code=404)
        doc_check.register_uri('POST', f'{client.db_uri}', status_code=201, json = {"rev":"362-6053b30578b8ca949d50ba125c76c4e9"})
        doc_check.register_uri('PUT', f'{client.db_uri}/{doc_id}/test.py', status_code=201)
        with open(__file__, 'rb') as fp:
            client.upload_file(fp, f'{doc_id}/test.py')

def test_upload_bytes_as_file():
    import json
    host = '127.0.0.1'
    port = '5984'
    database = 'test'
    connection_str = f'couchdb://{host}:{port}/{database}'
    doc_id = 'DOC'
    my_data = {
        'name': 'thanos'
    }
    attachment_file_name = 'takis/takis/catelog.json'
    client = CouchDBClient(connection_str)
    with requests_mock.Mocker() as doc_check:
        doc_check.register_uri('HEAD', f'{client.db_uri}/{doc_id}', status_code=404)
        doc_check.register_uri('POST', f'{client.db_uri}', status_code=201, json = {"rev":"362-6053b30578b8ca949d50ba125c76c4e9"})
        doc_check.register_uri('PUT', f'{client.db_uri}/{doc_id}/{attachment_file_name}', status_code=201)
        with open(__file__, 'rb') as fp:
            client.upload_bytes_file(bytes(json.dumps(my_data), 'utf-8'), f'{doc_id}/{attachment_file_name}')


def test_init_db_clean():
    import json
    host = '127.0.0.1'
    port = '5984'
    database = 'test'
    connection_str = f'couchdb://{host}:{port}/{database}'
    doc_id = 'DOC'
    my_data = {
        'name': 'thanos'
    }
    attachment_file_name = 'takis/takis/catelog.json'
    client = CouchDBClient(connection_str)
    with requests_mock.Mocker() as doc_check:
        doc_check.register_uri('HEAD', f'{client.db_uri}', status_code=404)
        doc_check.register_uri('PUT', f'{client.db_uri}')
        doc_check.register_uri('HEAD', f'{client.db_uri}/{client.COUCHFS_VIEWS["_id"]}', status_code=404)
        doc_check.register_uri('POST', f'{client.db_uri}', status_code=201,
                               json={"rev": "362-6053b30578b8ca949d50ba125c76c4e9"})
        with open(__file__, 'rb') as fp:
            client.init_db()