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

def test_no_connection_str_given():
    scheme = 'http'
    host = '127.0.0.1'
    port = '5984'
    database = 'test'
    db_uri = f'http://{host}:{port}/{database}'
    client = CouchDBClient()
    assert client.db_uri == db_uri

def test_no_connection_str():
    class NoConStr(CouchDBClient):
        URI_ENVIRON_KEY = 'XXXX'
    with pytest.raises(URLRequired):
        NoConStr()


def test_list_attchments_one_pattern():
    params = {'reduce': False, 'include_docs': False}
    with requests_mock.Mocker() as m:
        client = CouchDBClient()
        m.get(f'{client.db_uri}/_design/views/_view/attachment_list?reduce=false', json=attachment_list)
        assert len(list(client.list_attachments('doc-1'))) == 1

def test_list_attchments_two_patterns():
    with requests_mock.Mocker() as m:
        client = CouchDBClient()
        m.get(f'{client.db_uri}/_design/views/_view/attachment_list?reduce=false', json=attachment_list)
        assert len(list(client.list_attachments('doc-1','doc-2'))) == 2

def test_list_attchments_no_patterns():
    with requests_mock.Mocker() as m:
        client = CouchDBClient()
        m.get(f'{client.db_uri}/_design/views/_view/attachment_list?reduce=false', json=attachment_list)
        assert len(list(client.list_attachments())) == 3


def test_get_attachment():
    with CouchDBClient().get_attachment('http://127.0.0.1:5984/test/TAKIS/takis/takis/wsgi.py') as fp:
        assert len(fp.read()) == 387
        assert os.path.exists(fp.name)
    assert not os.path.exists(fp.name)



def test_get_attachment_in_memory():
    with CouchDBClient().get_attachment('http://127.0.0.1:5984/test/TAKIS/takis/takis/wsgi.py',in_memory=True) as buff:
        assert len(buff) == 387
    assert len(buff) == 387


def test_upload_file():
    doc_id = 'TAKIS'
    attachment_path='/takis/takis'
    some_file = os.path.basename(__file__)
    with open(__file__, 'rb') as fp:
        CouchDBClient().upload_file(fp, f'{doc_id}/{some_file}')


def test_upload_bytes_as_file():
    import json
    my_data = {
    'name': 'thanos'
    }
    doc_id = 'TAKIS'
    attachment_file_name = 'takis/takis/catelog.json'
    CouchDBClient().upload_bytes_file(bytes(json.dumps(my_data), 'utf-8'), f'{doc_id}/{attachment_file_name}')
