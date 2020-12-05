import os

from couchfs.couchfs import  CouchDBClient

def test_get_attachment():
    with CouchDBClient().get_attachment('http://127.0.0.1:5984/test/TAKIS/takis/takis/wsgi.py') as fp:
        assert len(fp.read()) == 387
        assert os.path.exists(fp.name)
    assert os.path.exists(fp.name) == False


def test_get_attachment_in_memory():
    with CouchDBClient().get_attachment('http://127.0.0.1:5984/test/TAKIS/takis/takis/wsgi.py',in_memory=True) as buff:
        assert len(buff) == 387
    assert len(buff) == 387
