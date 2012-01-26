#!/usr/bin/env pythone
import sys
import os
import traceback
from optparse import OptionParser

from bundle import HgBundle, GitBundle
from errors import BManError
import commands


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
                        bundle = bundle_types[bundle_type][1](name, url, False)
                        bundles[name] = bundle
                    except KeyError:
                        raise BundleError("Unknown bundle type:", bundle_type)

                bundle.tracked = True
                bundle.saved_revision = revision
                if bundle.url != url:
                    pass # XXX: do something here?


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



if __name__ == "__main__":
    bundles = {}
    bundle_types = {"git" : (".git", GitBundle), "hg" : (".hg", HgBundle)}

    # create a console
    from ui import Console
    console = Console()

    # usage is handy
    usage = "%prog <command> [args]\n\nCommands:\n"
    for name in sorted(commands.command_list.keys()):
        usage += "\t%s\n" % (name)


    # parse args
    parser = OptionParser(usage=usage, version="%prog 0.1")
    parser.add_option("-v", "--verbose", dest="verbose", action="store_true", default=False)
    parser.add_option("-a", "--all", help="operate on all bundles", dest="all", action="store_true", default=False)
    parser.add_option("-r", "--revision", help="operate on a particular revision", dest="revision", default=None)
    parser.add_option("-l", "--limit", help="limit output to a number of items", dest="limit", default=None)

    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit()
    elif sys.argv[1] != "--version":
        command = sys.argv.pop(1)

    (options, args) = parser.parse_args()

    # load bundles
    bundles = scan_repositories(bundle_types)
    load_tracking_data(bundles, bundle_types)

    # do it!
    try:
        commands.execute(command, console, bundles, options, args)
    except BManError, e:
        console.write("BManError: ")
        console.write_line(e, color="red")
        if options.verbose:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            for line in traceback.format_tb(exc_traceback):
                console.write_line(line, color="yellow")
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        console.write("UnknownError: ")
        console.write_line(exc_value, color="red")
        if options.verbose:
            for line in traceback.format_tb(exc_traceback):
                console.write_line(line, color="yellow")
