from __future__ import print_function, absolute_import, division

import logging

from sys import argv, exit
from time import time



from errno import ENOENT
from stat import S_IFDIR, S_IFLNK, S_IFREG
from sys import argv, exit

from fuse import Operations, LoggingMixIn



class FuseOperations(LoggingMixIn, Operations):
    '''
    A simple SFTP filesystem. Requires paramiko: http://www.lag.net/paramiko/
    You need to be able to login to remote host without entering a password.
    '''

    def __init__(self, storage):
        self.storage = storage

    def chmod(self, path, mode):
        return self.storage.chmod(path, mode)

    def chown(self, path, uid, gid):
        return self.storage.chown(path, uid, gid)

    def create(self, path, mode):
        return self.storage.create(path, mode)

    def destroy(self, path):
        return self.storage.destroy(path)

    def getattr(self, path, fh=None):
        return self.storage.getattr(path, fh)

    def mkdir(self, path, mode):
        return self.storage.mkdir(path, mode)

    def read(self, path, size, offset, fh):
        return self.storage.read(path, size, offset, fh)

    def readdir(self, path, fh):
        return self.storage.readdir(path, fh)

    def readlink(self, path):
        return self.storage.readlink(path)

    def rename(self, old, new):
        return self.storage.rename(old, new)

    def rmdir(self, path):
        return self.storage.rmdir(path)

    def symlink(self, target, source):
        return self.storage.symlink(target, source)

    def truncate(self, path, length, fh=None):
        return self.storage.truncate(path, length, fh)

    def unlink(self, path):
        return self.storage.unlink(path)

    def utimens(self, path, times=None):
        return self.storage.utimens(path, times)

    def write(self, path, data, offset, fh):
        return self.storage.write(path, data, offset, fh)

if __name__ == '__main__':
    if len(argv) != 3:
        print('usage: %s <host> <mountpoint>' % argv[0])
        exit(1)