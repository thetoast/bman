#!/usr/bin/env pythone
import sys
import os
from optparse import OptionParser

from bundle import HgBundle, GitBundle

class BManError(Exception): pass
class BundleError(BManError): pass


def load_tracking_data(bundles, bundle_types):

    if os.path.exists('.bundles'):
        for line in open('.bundles').read().split('\n'):
            if len(line):
                parts = line.split(' ')
                if len(parts) != 4:
                    raise BundleError("Invalid .bundles entry: %s" % (line))

                name, bundle_type, url, revision = parts
                bundle = None
                try:
                    bundle = bundles[name]
                except KeyError:
                    try:
                        bundle = bundle_types[bundle_type][1](name, url)
                    except KeyError:
                        raise BundleError("Unknown bundle type:", bundle_type)

                bundle.tracked = True
                bundle.saved_revision = revision
                if bundle.url != url:
                    print "Updating bundle url for", name
                    print "\t", bundle.url, " -> ", url
                    bundle.url = url


def scan_repositories(bundle_types, repos=None):
    bundles = {}

    if not repos:
        names = os.listdir('.')

    for name in names:
        if os.path.isdir(name):
            for dir_name, bundle_type in bundle_types.values():
                if os.path.isdir(os.path.join(name, dir_name)):
                    bundles[name] = bundle_type(name)


    return bundles


def list_(console, bundles, options, args):
    maxname = max(len(name) for name in bundles.keys())
    for name, bundle in bundles.items():
        console.write("%s" % (name), "red")
        if bundle.tracked:
            console.write("* ")
        else:
            console.write("  ")
        console.write(" "*(maxname - len(name)))
        console.write("%s " % (bundle.head), "yellow")
        console.write("%s " % (bundle.url), "magenta")
        console.write("\n")

def heads(console, bundles, options, args):
    pass
def detail(console, bundles, options, args):
    pass
def urls(console, bundles, options, args):
    pass



def add(console, bundles, options, args):
    if len(args) == 0 and not options.all:
        raise BManError("No bundles specified")

    if options.all:
        names = bundles.keys()
    else:
        names = args

    for name in names:
        try:
            bundle = bundles[name]
        except KeyError:
            raise BManError("Bundle %s not found" % (name))

        if not bundle.tracked:
            print "Adding bundle", name
            with open('.bundles', 'a') as fd:
                fd.write('%s %s %s %s\n' % (bundle.name, bundle.vcs, bundle.url, bundle.head))


def remove(console, bundles, options, args):
    if len(args) == 0 and not options.all:
        raise BManError("No bundles specified")

    if options.all:
        names = bundles.keys()
    else:
        names = args

    with open('.bundles', 'r+') as fd:
        lines = fd.readlines()
        fd.seek(0)
        fd.truncate()
        for line in lines:
            name = line.split(' ')[0]
            if name in names:
                print "Removing bundle", name
            else:
                fd.write(line)


def pull(console, bundles, options, args):
    pass
def update(console, bundles, options, args):
    pass
def init(console, bundles, options, args):
    pass

usage = """ %prog <command> [args]

Commands:
   list
   heads
   detail
   urls
   add
   remove
   pull
   update"""


valid_commands = {
    "list"   : list_,
    "heads"  : heads,
    "detail" : detail,
    "urls"   : urls,
    "add"    : add,
    "remove" : remove,
    "pull"   : pull,
    "update" : update,
    "init" : init,
}


if __name__ == "__main__":
    bundles = {}
    bundle_types = {"git" : (".git", GitBundle), "hg" : (".hg", HgBundle)}

    from ui import Win32Console
    console = Win32Console()

    parser = OptionParser(usage=usage, version="%prog 0.1")
    parser.add_option("-v", "--verbose", dest="verbose", action="store_true", default=False)
    parser.add_option("-a", "--all", dest="all", action="store_true", default=False)

    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit()
    elif sys.argv[1] != "--version":
        command = sys.argv.pop(1)

    (options, args) = parser.parse_args()

    if command not in valid_commands.keys():
        print "Invalid command:", command
        parser.print_help()
        sys.exit()

    bundles = scan_repositories(bundle_types)
    load_tracking_data(bundles, bundle_types)


    try:
        valid_commands[command](console, bundles, options, args)
    except BManError, e:
        print "BManError:", e
