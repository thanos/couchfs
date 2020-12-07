from __future__ import print_function, absolute_import, division

from sys import argv, exit

from refuse.high import Operations, LoggingMixIn


class FuseOperations(LoggingMixIn, Operations):
    '''
    A simple SFTP filesystem. Requires paramiko: http://www.lag.net/paramiko/
    You need to be able to login to remote host without entering a password.
    '''

    def __init__(self, storage):
        self.storage = storage

    def chmod(self, path, mode):
        raise NotImplemented()

    def chown(self, path, uid, gid):
        raise NotImplemented()

    def create(self, path, mode):
        raise NotImplemented()

    def destroy(self, path):
        raise NotImplemented()

    def getattr(self, path, fh=None):
        raise NotImplemented()

    def mkdir(self, path, mode):
        raise NotImplemented()

    def read(self, path, size, offset, fh):
        raise NotImplemented()

    def readdir(self, path, fh):
        raise NotImplemented()

    def readlink(self, path):
        raise NotImplemented()

    def rename(self, old, new):
        raise NotImplemented()

    def rmdir(self, path):
        raise NotImplemented()

    def symlink(self, target, source):
        raise NotImplemented()

    def truncate(self, path, length, fh=None):
        raise NotImplemented()

    def unlink(self, path):
        raise NotImplemented()

    def utimens(self, path, times=None):
        raise NotImplemented()

    def write(self, path, data, offset, fh):
        raise NotImplemented()



if __name__ == '__main__':
    if len(argv) != 3:
        print('usage: %s <host> <mountpoint>' % argv[0])
        exit(1)