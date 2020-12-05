import os

from couchfs.commands import  CouchDBClient

def test_get_attachment():
    couch_uri ='couchdb://admin:R30d5tar%@127.0.0.1:5984/test'
    with CouchDBClient(couch_uri).get_attachment('http://127.0.0.1:5984/test/TAKIS/takis/takis/wsgi.py') as fp:
        assert len(fp.read()) == 387
        assert os.path.exists(fp.name)
    assert os.path.exists(fp.name) == False


def test_get_attachment_in_memory():
    couch_uri ='couchdb://admin:R30d5tar%@127.0.0.1:5984/test'
    with CouchDBClient(couch_uri).get_attachment('http://127.0.0.1:5984/test/TAKIS/takis/takis/wsgi.py',in_memory=True) as buff:
        assert len(buff) == 387
    assert len(buff) == 387