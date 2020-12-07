"""
A  client api for couchdb attachments

"""

"""Main module."""
import logging
import fnmatch
import io
import mimetypes
import os
import pathlib
import re
import tempfile
from contextlib import contextmanager

import requests

logger = logging.getLogger(__file__)
echo = logger.info

class CouchDBClientException(Exception):
    def __init__(self, *args, **kwargs):
        super(CouchDBClientException, self).__init__(*args, **kwargs)


class URLRequired(CouchDBClientException):
    """A valid URL is required."""


class BadConnectionURI(CouchDBClientException):
    """A valid URL is required."""


class CouchDBClient:
    URI_ENVIRON_KEY = 'COUCHDB_URI'
    CONNECTION_RE = 'couchdb(s)?://((\w+)\:(.+)@)?([\w\.]+)(:(\d+))?/(\w+)'
    URI_RE = re.compile(CONNECTION_RE)

    def __init__(self, uri=None):
        if uri is None:
            uri = os.environ.get(self.URI_ENVIRON_KEY)
        if not uri:
            key = self.URI_ENVIRON_KEY
            raise URLRequired(f'You can set environment varialble {key}')
        scheme, userid, psswd, host, port, db = self.parse_connection_uri(uri)
        if userid and psswd:
            self.auth = (userid, psswd)
        else:
            self.auth = None
        self.db = db
        self.db_uri = f'{scheme}://{host}{port}/{self.db}'

    def check_db(self):
        response = requests.head(f"{self.db_uri}", auth=self.auth)
        return response.status_code == 200

    def create_db(self):
        response = requests.put(f"{self.db_uri}", auth=self.auth)
        response.raise_for_status()

    def save_doc(self, doc):
        _id = doc['_id']
        doc_uri = f'{self.db_uri}/{_id}'
        response = requests.head(doc_uri, auth=self.auth)
        if response.status_code == 200:
            rev = response.headers['ETag']
            headers = {'If-Match': rev[1:-1]}
            response = requests.put(doc_uri, json=doc, headers=headers, auth=self.auth)
        elif response.status_code == 404:
            response = requests.post(self.db_uri, json=doc, auth=self.auth)
        response.raise_for_status()


    def parse_connection_uri(self, uri):
        """
        Given:
        'couchdb://admin:*****%@127.0.0.1:5984/test' -> http://127.0.0.1:5984/
        :param uri:
        :return {host, db, auth, passwd}:
        """
        if match := self.URI_RE.match(uri):
            (ssl, _, userid, psswd, host, _, port, db) = match.groups()
            scheme = 'http' + ('s' if ssl else '')
            port = f':{port}' if port else ''
            return scheme, userid, psswd, host, port, db
        else:
            raise BadConnectionURI(f'use a connections like {self.CONNECTION_RE}')

    def list_attachments(self, *patterns):
        regexs = []
        for pattern in patterns:
            if self.WILDCARD_RE.search(pattern):
                regex = re.compile(fnmatch.translate(pattern))
            else:
                regex = re.compile(fnmatch.translate(pattern)[:-2])
            regexs.append(regex)
        for file_path, file_size in self.run_view():
            if not regexs or any([regex.search(file_path) for regex in regexs]):
                yield file_path, file_size

    def run_view(self, **args):
        params = {'reduce': False, 'include_docs': False}
        if 'depth' in args:
            params['group_level'] = args['depth']
            params['reduce'] = True
        response = requests.get(f"{self.db_uri}/_design/couchfs_views/_view/attachment_list", params=params, auth=self.auth)
        response.raise_for_status()
        for doc in response.json()['rows']:
            yield '/'.join(doc['key']), doc['value']

    def download(self, src, dst, dry_run=False):
        for src, dst in self.download_srcdst(src, dst):
            if dry_run:
                yield src, dst, 'DRY RUN', response
            else:
                uri = f'{self.db_uri}/{src}'
                response = requests.get(uri, auth=self.auth)
                yield uri, dst, response.status_code, response.reason

    WILDCARD_RE = re.compile('[\*\?\[\]]+')

    def download_srcdst(self, src, dst, dry_run=False):
        if match := self.WILDCARD_RE.search(src):
            regex = re.compile(fnmatch.translate(src))
            is_copying_files = True
        else:
            regex = re.compile(fnmatch.translate(src)[:-2])
            sub_regex = re.compile(src)

            is_copying_files = False
        for file_path, _ in self.ls():
            if regex.search(file_path):
                if is_copying_files:
                    match = self.WILDCARD_RE.search(src)
                    dst_file_path = file_path[match.span()[0]:]
                    if dst_file_path.startswith('/'):
                        dst_file_path = file_path[1:]
                    dest_path = os.path.join(dst, dst_file_path)
                else:
                    dst_file_path = file_path[len(src):]
                    if file_path.startswith('/'):
                        dst_file_path = dst_file_path[1:]
                    dest_path = os.path.join(dst, dst_file_path[1:])
                if not dest_path.startswith('dump'):
                    print('NO DUMP', is_copying_files, dst, file_path[len(src):])
                    # break
                yield file_path, dest_path

    def download_file(self, url, dest):
        with open(dest, 'wb') as f:
            return self.download_to_file(url, f)

    def download_to_file(self, url, file_obj):
        with requests.get(url, stream=True, auth=self.auth) as r:
            r.raise_for_status()
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    file_obj.write(chunk)

    @contextmanager
    def get_attachment(self, url, in_memory=False):
        try:
            if in_memory:
                bytes_fp = io.BytesIO()
                self.download_to_file(url, bytes_fp)
                yield bytes_fp.getvalue()
            else:
                fp = tempfile.NamedTemporaryFile(delete=False)
                self.download_to_file(url, fp)
                fp.close()
                yield open(fp.name, 'rb')
        finally:
            if in_memory:
                bytes_fp.close()
            else:
                os.unlink(fp.name)

    def get_attachment_as_bytes(self, url):
        return requests.get(url, stream=True, auth=self.auth).content

    def upload(self, src, dst, dry_run=False):
        src = os.path.abspath(src)
        if os.path.isfile(src):
            if dry_run:
                yield src, dst, 'DRY RUN', ''
            else:
                yield self.upload_file(src, os.path.join(dst, os.path.basename(src)))
        elif os.path.isdir(src):
            p = pathlib.Path(src).resolve()
            for (dirpath, dirs, files) in os.walk(src):
                for filename in files:
                    file_path = os.path.join(dirpath, filename)
                    pp = file_path[len(p.parent.as_posix()) + 1:]
                    dest_path = os.path.join(dst, pp)
                    if dry_run:
                        yield file_path, dest_path, 'DRY RUN', ''
                    else:
                        yield self.upload_file(file_path, dest_path)

    def upload_bytes_file(self, src_bytes, dst):
        with tempfile.NamedTemporaryFile() as src_fp:
            src_fp.name = os.path.basename(dst)
            src_fp.write(src_bytes)
            return self.upload_file(src_fp, dst)

    def upload_file(self, src, dst):
        """
        Uploads a file using dst as the doc/bucket id
        :param src: path to file to upload
        :param dst: id
        :return: file_name, file_url, upload status, upload message
        """
        doc_id = [segment for segment in dst.split('/') if segment][0]
        file_name = '/'.join(dst.split('/')[1:])
        doc_uri = f'{self.db_uri}/{doc_id}'
        file_uri = f'{doc_uri}/{file_name}'
        response = requests.head(f'{doc_uri}', auth=self.auth)
        if response.status_code == 404:
            response = requests.post(f'{self.db_uri}', json=dict(_id=doc_id), auth=self.auth)
            if response.status_code != 201:
                return file_name, f'{file_uri}', response.status_code, response.reason
            rev = response.json()['rev']
        else:
            rev = response.headers['ETag']
        major, _ = mimetypes.guess_type(src.name)
        headers = {'Content-type': f'{major}', 'If-Match': rev[1:-1]}
        response = requests.put(f'{file_uri}', data=src, headers=headers, auth=self.auth)
        response.raise_for_status()
        return file_name, f'{file_uri}', response.status_code, response.reason


    @classmethod
    def init_db(cls, logger=echo):
        echo('connecting to couchdb')
        client = cls()
        logger('checking the db')
        if not client.check_db():
            logger('creating the db')
            client.create_db()
        _id = client.COUCHFS_VIEWS['_id']
        logger(f'creating or updating the db {_id}')
        client.save_doc(client.COUCHFS_VIEWS)
        logger(f'db is now setup')

    COUCHFS_VIEWS={
      "_id": "_design/couchfs_views",
      "views": {
        "attachment_list": {
          "map": "function (doc) {\n if (doc._attachments) {\n   for (const file_name in doc._attachments) {\n      emit((doc._id+'/'+file_name).split('/'), doc._attachments[file_name].length);\n  }\n} else {\n  emit(doc._id.split('/'), 0)\n}\n}",
          "reduce": "_stats"
        }
      },
      "language": "javascript"
    }