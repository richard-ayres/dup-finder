#!/usr/bin/env python2 -W all
"""This program searches python files for duplicate functions and classes"""
import sys
import os
import re
from collections import defaultdict

DEFAULT_PATH = './'


class DupFinder(object):
    """This class searches python files for duplicate functions and classes"""

    def __init__(self, path):
        self.path = path
        self.exclude_dirs = ['.git', 'vendor']

        # This is a database of class and function definitions, with a list of
        # the filenames in which they were each found
        self.found = {
            # function names pointing to a list of their files
            'def': defaultdict(list),
            # class names pointing to a list of their files
            'class': defaultdict(list)
        }

        # Useful regexes that we will use later
        self.rx_python = re.compile(r'\.py$')
        self.rx_definition = re.compile(r'^(def|class)\s+(\w+)\(')

    def _find_files(self, path=None):
        """Find all python files in the given subdirectory, or use the path
        given in the constructor. Returns a list of python file names."""
        if path is None:
            path = self.path

        # Listing of current directory
        listing = [os.path.join(path, fn)
                   for fn in os.listdir(path)]

        # List of python files
        filenames = []

        for filename in listing:
            # Is filename a directory?
            if os.path.isdir(filename) and filename not in self.exclude_dirs:
                filenames.extend(self._find_files(filename))

            # Is it a python file?
            elif self.rx_python.search(filename):
                filenames.append(filename)

        return filenames

    def _add_definition(self, typ, name, filename):
        """Add the given line description and filename to our database of
        classes and function definitions."""
        self.found[typ][name].append(filename)

    def _process_line(self, filename, line):
        """Search for a definition on this line. If it is a definition, extract
        it and add it to the database"""
        match = self.rx_definition.match(line)
        if match:
            self._add_definition(match.group(1), match.group(2), filename)

    def find_definitions(self, path=None):
        """Find all function and class definitions in all python files below
        the given path"""
        if path is None:
            path = self.path

        # For each python file, read it line by line and add all class and
        # function definitions to our database
        for filename in self._find_files(path):
            with open(filename, 'r') as handle:
                for line in handle:
                    self._process_line(filename, line)

    def _do_show_dups(self, typ):
        """Show duplicates of the given definition type"""

        # f is a tuple of (string, list), the string is the name of the object,
        # the list is of files containing the object
        multiples = [f for f in self.found[typ].iteritems() if len(f[1]) > 1]

        if not multiples:
            print "\tNone"
            return

        for name, files in multiples:
            print "%s: " % (name,)
            for filename in files:
                print "\t%s" % (filename,)

    def show_dups(self):
        """Show duplicate functions and classes on the output"""
        print "Functions:"
        self._do_show_dups('def')

        print "\nClasses:"
        self._do_show_dups('class')


def main():
    """main() function"""
    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        path = DEFAULT_PATH

    dup_finder = DupFinder(path)
    dup_finder.find_definitions()
    dup_finder.show_dups()

if __name__ == '__main__':
    main()
