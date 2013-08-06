#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
    ###-> pycopy script <-###

usage: python pycopy.py [-f|-w|-x] <src_path> [<src_path>, ...] <dst_path>

    -h (--help) prints this help

    -f (--force-overwrite) force copy (overwrite read-only files)

    -w (--without-empty-dirs) recursive copy without empty directories

    -x (--delete-source) after successful copy, source path is deleted
'''

import getopt
import os
import os.path
import shutil
import stat
import sys


class Pycopy:

    def __init__(self, options):

        if 'force-overwrite' in options:
            self.remove_read_only_flag = lambda x: Pycopy.__remove_read_only_flag(x)
        else:
            self.remove_read_only_flag = lambda x: None

        self.no_empty_dirs = True if 'without-empty-dirs' in options else False
        self.dst_is_dir = True if 'destination-is-directory' in options else False
        self.del_src = True if 'delete-source' in options else False
        self.any_error = False

            
    def copy(self, src, dst):
        self.any_error = False
        self.__copy(src, dst)

        if self.del_src and not self.any_error:
            try:
                if os.path.isdir(src):
                    shutil.rmtree(src)
                else:
                    os.remove(src)
            except Exception, e:
                sys.stdout.write('[Errno %d], %s: \'%s\'\n', (e.errno, e.strerror, e.filename))
            
    def __copy(self, src, dst):

        if os.path.exists(src):
            if os.path.isfile(src):
                self.__copy_file(src, dst)
            elif os.path.isdir(src):
                self.__copy_dir(src, dst)
        else:
            self.__yeld('Source path: "%s" does not exists\n', src)


    def __copy_file(self, src, dst):

        if os.path.exists(dst):
            if os.path.isdir(dst):
                dst = os.path.join(dst, os.path.basename(src))
        else:
            directory_to_create = None
            
            if self.dst_is_dir or dst[-1] == '/' or dst[-1] == '\\':
                directory_to_create = dst
                dst = os.path.join(dst, os.path.basename(src))
            else:
                if not os.path.exists(os.path.dirname(dst)):
                    directory_to_create = os.path.dirname(dst)

            if directory_to_create:
                try:
                    os.makedirs(directory_to_create)
                except Exception, e:
                    self.__yeld('[Errno %d], %s: \'%s\'\n', (e.errno, e.strerror, e.filename))
                    return

        if os.path.exists(dst) and os.path.isfile(dst):
            self.remove_read_only_flag(dst)

        try:
            sys.stdout.write('\n%s >>> %s\n' % (src, dst))
            shutil.copy2(src, dst)
            sys.stdout.write('\tFile copied\n')
        except Exception, e:
            self.__yeld('\t[Errno %d], %s: \'%s\'\n', (e.errno, e.strerror, e.filename))


    def __copy_dir(self, src, dst):

        l = os.listdir(src)

        if self.no_empty_dirs and len(l) == 0:
            return

        if src[-1] != '/' or src[-1] != '\\':
            dst = os.path.join(dst, os.path.basename(src))
            
        if not os.path.exists(dst):
            try:
                os.makedirs(dst)
            except Exception, e:
                self.__yeld('[Errno %d], %s: \'%s\'\n', (e.errno, e.strerror, e.filename))
                return

        for f in l:
            self.__copy(os.path.join(src, f), dst)


    def __yeld(self, text, args):
        self.any_error = True
        sys.stderr.write(text % args)


    @staticmethod
    def __remove_read_only_flag(file_path):

        mode = os.stat(file_path).st_mode
        if not mode & stat.S_IWRITE:
            os.chmod(file_path, stat.S_IWRITE)

    #~class Pyxcopy


def pycopy(sources, destination, options=()):

    if len(sources) > 1:
        options += 'destination-is-directory',

    pc = Pycopy(options)

    for source in sources:
        pc.copy(source, destination)

   
if __name__ == '__main__':

    options = ()
    sources = ()
    destination = ''

    longopts  = ['help',
                 'force-overwrite',
                 'without-empty-dirs',
                 'delete-source',
                 ]

    shortopts = 'hfwx'

    param_h = ['-h', '--help']
    param_f = ['-f', '--force-overwrite']
    param_w = ['-w', '--without-empty-dirs']
    param_x = ['-x', '--delete-source']

    try:
        opts, args = getopt.getopt(sys.argv[1:], shortopts, longopts)
    except getopt.GetoptError:
        sys.stderr.write('Error: wrong parameters!\nUse \'--help\' option.\n')
        sys.exit(1)

    for opt, arg in opts:

        if opt in param_h:
            sys.stderr.write(__doc__)
            sys.exit(1)

        elif opt in param_f:
            options += param_f[1][2:],

        elif opt in param_w:
            options += param_w[1][2:],

        elif opt in param_x:
            options += param_x[1][2:],

        else:
            sys.stderr.write('Error: unknown options %s %s\nUse \'--help\' option.\n' % (opt, arg))
            sys.exit(1)

    if len(args) < 2:
        sys.stderr.write('Error: Not enough parameters!\nUse \'--help\' option.\n')
        sys.exit(1)

    for s in args[:-1]:
        sources += s,
    destination = args[-1]

    pycopy(sources, destination, options)

    sys.exit(0)

