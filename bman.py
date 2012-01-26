import sys
import os
from subprocess import Popen, PIPE
from ConfigParser import SafeConfigParser, NoSectionError
from optparse import OptionParser

class BManError(Exception): pass
class BundleError(BManError): pass

class Bundle(object):
    def __init__(self, repo, url="", scan=True):
        self.repo = repo
        self.tracked=False
        self.saved_revision=""
        self.head=""
        self.tip=""
        self.status="unknown"
        self.url=url

        if scan:
            self.scan()

    def scan(self):
        self.url = self.get_url()
        self.head = self.get_head()
        self.tip = self.get_tip()

    def get_url(self):
        return ""

    def get_head(self, verbose=False):
        return ""

    def get_tip(self, verbose=False):
        return ""

    def pull(self, verbose=False):
        pass

    def update(self, verbose=False):
        pass

    def __str__(self):
        return "%s-%s-%s-%s-%s-%s-%s-%s" % (self.repo, type(self), self.tracked, self.saved_revision, self.head, self.tip, self.status, self.url)

    def __repr__(self):
        return self.__str__()



class HgBundle(Bundle):
    def get_url(self):
        config = SafeConfigParser()
        config.read('%s/.hg/hgrc' % (self.repo))

        try:
            section = dict(config.items('paths'))

            try:
                self.url = section['default.pull']
            except KeyError: pass

            url = section['default']
        except KeyError:
            raise BundleError("Unable to determine bundle url for %s" % (self.repo))
        except NoSectionError:
            raise BundleError("Unable to determine bundle url for %s" % (self.repo))

        return url

    def get_head(self):
        p = Popen(['hg', '-R', self.repo, 'parent','--template={node}'], stdout=PIPE)
        head = p.communicate()[0].strip()

        return head

    def get_tip(self):
        p = Popen(['hg', '-R', self.repo, 'log', '-r', 'tip', '-l1', '--template={node}'], stdout=PIPE)
        tip = p.communicate()[0].strip()

        return tip


class GitBundle(Bundle):
    def get_url(self):
        os.chdir(self.repo)
        try:
            p = Popen(['git', 'config','remote.origin.url'], stdout=PIPE, shell=True)
            url = p.communicate()[0].strip()
            p.wait()
        except Exception, e:
            raise BundleError(e)
        finally:
            os.chdir('..')

        return url

    def get_head(self):
        os.chdir(self.repo)
        try:
            p = Popen(['git', 'log','-n1', 'HEAD', '--format=%H'], stdout=PIPE, shell=True)
            head = p.communicate()[0].strip()
            p.wait()
        except Exception, e:
            raise BundleError(e)
        finally:
            os.chdir('..')

        return head

    def get_tip(self):
        os.chdir(self.repo)
        try:
            p = Popen(['git', 'log','-n1', 'master', '--format=%H'], stdout=PIPE, shell=True)
            tip = p.communicate()[0].strip()
            p.wait()
        except Exception, e:
            raise BundleError(e)
        finally:
            os.chdir('..')

        return tip


def load_tracking_data(bundles, bundle_types):

    if os.path.exists('.bundles'):
        for line in open('.bundles').read().split('\n'):
            if len(line):
                parts = line.split(' ')
                if len(parts) != 4:
                    raise BundleError("Invalid .bundles entry: %s" % (line))

                repo, bundle_type, url, revision = parts
                bundle = None
                try:
                    bundle = bundles[repo]
                except KeyError:
                    try:
                        bundle = bundle_types[bundle_type][1](repo, url)
                    except KeyError:
                        raise BundleError("Unknown bundle type:", bundle_type)

                bundle.tracked = True
                bundle.saved_revision = revision
                if bundle.url != url:
                    print "Updating bundle url for", repo
                    print "\t", bundle.url, " -> ", url
                    bundle.url = url


def scan_repositories(bundle_types):
    bundles = {}

    for repo in os.listdir('.'):
        if os.path.isdir(repo):
            for dir_name, bundle_type in bundle_types.values():
                if os.path.isdir(os.path.join(repo, dir_name)):
                    bundles[repo] = bundle_type(repo)


    return bundles


def list_(bundles, options, args):
    pass
def heads(bundles, options, args):
    pass
def detail(bundles, options, args):
    pass
def urls(bundles, options, args):
    pass
def add(bundles, options, args):
    pass
def remove(bundles, options, args):
    pass
def pull(bundles, options, args):
    pass
def update(bundles, options, args):
    pass
def init(bundles, options, args):
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

    parser = OptionParser(usage=usage, version="%prog 0.1")
    parser.add_option("-v", "--verbose", dest="verbose", action="store_true", default=False)

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


    valid_commands[command](bundles, options, args)
