# couchfs
a couchdb user space (FUSE) file system plus a cli for treating couchdb databases as a file system drives


[![Pypi Status](https://img.shields.io/pypi/v/couchfs.svg)](https://pypi.org/pypi/couchfs/) 
[![Build Status](https://travis-ci.com/thanos/couchfs.svg?branch=master)](https://travis-ci.com/thanos/couchfs)
[![Docs Status](https://readthedocs.org/projects/couchfs/badge/?version=latest)](https://couchfs.readthedocs.io/en/latest/) 
[![Coverage Status](https://coveralls.io/repos/github/thanos/couchfs/badge.svg?branch=master)](https://coveralls.io/github/thanos/couchfs?branch=master)

 * Free software: MIT license
 
## Features

## First the simple utils

### `couchfs ls`

`couchfs ls` let's you list the attachements in a couchdb database.
Just running ls without and path will give you the atatchments in every document in your database.



```shell script
export CouchDBClient_URI=couchdb://xxx:xxx@127.0.0.1:5984/myrepo

% couchfs ls 

TAKIS/takis/takis/asgi.py                             387 Bytes
TAKIS/takis/takis/settings.py                         3.8 kB
TAKIS_1/takis/takis/urls.py                           470 Bytes
```
Where `TAKIS`, `TAKIS_1`, `TAKIS_2` are the ids of different documents.
You can spec a path starting with the document `id`.

```shell script
% couchfs ls  TAKIS_2
TAKIS_2/takis/takis/wsgi.py                           470 Bytes
```

### `couchfs upload`

This allows to upload and attach files documents to couchdb document. It follows closely the sematics of GNU `cp -R`.
So when doing `couchfs upload source destination`, source will match what you want to copy, going recursively, and desitnation is a path starting with the document `id`.

```shell script
% couchfs upload ~/takis/all.json /TAKIS_1/

/Users/thanos/all.json http://127.0.0.1:5984/test/TAKIS_1/TAKIS_1/all.json 201:Created

```

There is a --dry_run flag that can save your ass!

```shell script
% couchfs upload ~/takis/takis /TAKIS_1/

/Users/thanos/takis/takis/media/dl131.jpg /TAKIS_1/takis/media/dl131.jpg DRY RUN:
/Users/thanos/takis/takis/media/vs233.jpg /TAKIS_1/takis/media/vs233.jpg DRY RUN:
/Users/thanos/takis/takis/media/tavsi098.jpg /TAKIS_1/takis/media/tavsi098.jpg DRY RUN:
/Users/thanos/takis/takis/media/mw042_on6H5f6.jpg /TAKIS_1/takis/media/mw042_on6H5f6.jpg DRY RUN:
/Users/thanos/takis/takis/media/t126.jpg /TAKIS_1/takis/media/t126.jpg DRY RUN:
/Users/thanos/takis/takis/media/tad040.jpg /TAKIS_1/takis/media/tad040.jpg DRY RUN:
```

### `couchfs download`

This allows to download files that are attached to couchdb documents. It follows closely the sematics of GNU `cp -R`.
So when doing `couchfs down source destination`, source will docuemnt id followed by a synthetic 
path, and desitnation is a local path and its directory tree will be created as necassery. Again there is a useful 
--dry_run flag.


```shell
% couchfs upload ~/takis/takis /TAKIS_1/

/Users/thanos/takis/takis/media/dl131.jpg /TAKIS_1/takis/media/dl131.jpg DRY RUN:
/Users/thanos/takis/takis/media/vs233.jpg /TAKIS_1/takis/media/vs233.jpg DRY RUN:
/Users/thanos/takis/takis/media/tavsi098.jpg /TAKIS_1/takis/media/tavsi098.jpg DRY RUN:
/Users/thanos/takis/takis/media/01-MOUSEIO_KATO_202002191257-00_02_01.png /TAKIS_1/takis/media/01-MOUSEIO_KATO_202002191257-00_02_01.png DRY RUN:
/Users/thanos/takis/takis/media/d023.jpg /TAKIS_1/takis/media/d023.jpg DRY RUN:
/Users/thanos/takis/takis/media/mw042_on6H5f6.jpg /TAKIS_1/takis/media/mw042_on6H5f6.jpg DRY RUN:
/Users/thanos/takis/takis/media/t126.jpg /TAKIS_1/takis/media/t126.jpg DRY RUN:
/Users/thanos/takis/takis/media/tad040.jpg /TAKIS_1/takis/media/tad040.jpg DRY RUN:
```

```shell script
%couchfs  download TAKIS/takis/takis/*.py dump

hhttp://127.0.0.1:5984/test/TAKIS/takis/takis/__init__.py dump/__init__.py 200:OK
http://127.0.0.1:5984/test/TAKIS/takis/takis/asgi.py dump/asgi.py 200:OK
http://127.0.0.1:5984/test/TAKIS/takis/takis/settings.py dump/settings.py 200:OK
http://127.0.0.1:5984/test/TAKIS/takis/takis/urls.py dump/urls.py 200:OK
http://127.0.0.1:5984/test/TAKIS/takis/takis/wsgi.py dump/wsgi.py 200:OK
```

## Utilities API


### Authentification

Option 1 set up an environment variable is the form
```shell script
export COUCHDB_URI='couchdb://username:password@host:port/database'
```

Or pass the connection string to `CouchDBClient` 
```python
from couchfs.couchfs import CouchDBClient

connection_str = 'couchdb://username:password@host:port/database'
CouchDBClient(connection_str)
```

if you whant to use another environment key you can always subclass `CouchDBClient`

```python
from couchfs.couchfs import CouchDBClient
class MyClient(CouchDBClient):
    URI_ENVIRON_KEY='MY_COUCHDB_URI'
```




### Fetching an attachment as a file 

You can use `CouchDBClient().get_attachment` to get a file handle on couchdb attachment. Attachments can be very big 
so they are streamed down into a temporary file that is released when you exit the context.

```python
import pandas as pd
from requests.exceptions import RequestException
from couchfs.couchfs import CouchDBClient, CouchDBClientException

doc_id = 'TAKIS'
doc_name = 'takis/takis/catelog.csv'
couch_uri ='couchdb://user:****@127.0.0.1:5984/test'
try:
  with CouchDBClient(couch_uri).download_file(f'{doc_id}/{doc_name}') as csvfile:
    expenses = pd.read_csv(csvfile)
except  (CouchDBClientException, RequestException) as error:  
    print(error)
```
### Fetching an attachment as bytes

For those who like to use their memory...

```python
import json
from couchfs.couchfs import CouchDBClient

doc_id = 'TAKIS'
doc_name = 'takis/takis/catelog.json'                                      
with CouchDBClient().download_file(f'{doc_id}/{doc_name}', in_memory=True) as somejson:
    expenses = json.loads(somejson)
```

### Fetching an attachment as bytes

For those who like to use their memory...

```python
import json
from couchfs.couchfs import CouchDBClient

doc_id = 'TAKIS'
doc_name = 'takis/takis/catelog.json'                                      
with CouchDBClient().download_file(f'{doc_id}/{doc_name}', in_memory=True) as somejson:
    expenses = json.loads(somejson)
```

### Fetching a list of attachment urls

```python
import json
from couchfs.couchfs import CouchDBClient

doc_id = 'TAKIS'              
for url in CouchDBClient().attachments(f'{doc_id}/*.json'):
    with CouchDBClient().download_file(url, in_memory=True) as somejson:
        process(somejson)
```

### Downloading a whole load of attachmenst

```python
import json
from couchfs.couchfs import CouchDBClient

doc_id = 'TAKIS'
attachments_path='/takis/takis'
destination = '/var/data'
CouchDBClient().download(f'{doc_id}/{attachments_path}', destination)
```



### Uploading an attachment

```python
from couchfs.couchfs import CouchDBClient

doc_id = 'TAKIS'
attachment_path='/takis/takis'
some_file = 'takis/takis/catelog.json'
with open(some_file, 'rb') as fp:
    CouchDBClient().upload_file(fp, f'{doc_id}/{attachment_path}')
```


### Uploading bytes as attachment

```python
import json
from couchfs.couchfs import CouchDBClient
my_data = {
'name': 'thanos'
}
doc_id = 'TAKIS'
attachment_file_name = 'takis/takis/catelog.json'
CouchDBClient().upload_bytes_file(json.dumps(my_data), f'{doc_id}/{attachment_file_name}')
```

### Uploading a load of files

```python
import json
from couchfs.couchfs import CouchDBClient

source='/User/thanos/takis'
doc_id = 'TAKIS'
CouchDBClient().upload(source, doc_id)
```

