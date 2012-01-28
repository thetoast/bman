from ConfigParser import SafeConfigParser, NoSectionError
from subprocess import Popen, PIPE
import os

from errors import BManError

class BundleError(BManError): pass

class Bundle(object):
    def __init__(self, name, url="", scan=True):
        self.name = name
        self.tracked=False
        self.installed=False
        self.saved_revision=""
        self.head=""
        self.tip=""
        self.status="unknown"
        self.url=url
        self.vcs=""

        if scan:
            self.scan()

    def scan(self):
        if os.path.isdir(self.name):
            self.installed=True
            self.url = self.get_url()
            self.head = self.get_head()
            self.tip = self.get_tip()

    def get_url(self):
        return ""

    def get_head(self):
        return ""

    def get_tip(self):
        return ""

    def pull(self):
        pass

    def update(self):
        pass

    def init(self):
        pass

    def __str__(self):
        return "%s-%s-%s-%s-%s-%s-%s-%s" % (self.name, type(self), self.tracked, self.saved_revision, self.head, self.tip, self.status, self.url)

    def __repr__(self):
        return self.__str__()



class HgBundle(Bundle):
    def __init__(self, *args, **kwargs):
        Bundle.__init__(self, *args, **kwargs)
        self.vcs = "hg"

    def get_url(self):
        config = SafeConfigParser()
        config.read('%s/.hg/hgrc' % (self.name))

        try:
            section = dict(config.items('paths'))

            try:
                self.url = section['default.pull']
            except KeyError: pass

            url = section['default']
        except KeyError:
            raise BundleError("Unable to determine bundle url for %s" % (self.name))
        except NoSectionError:
            raise BundleError("Unable to determine bundle url for %s" % (self.name))

        return url

    def get_head(self):
        p = Popen(['hg', '-R', self.name, 'parent','--template={node}'], stdout=PIPE)
        return p.communicate()[0].strip()

    def get_tip(self):
        p = Popen(['hg', '-R', self.name, 'log', '-r', 'tip', '-l1', '--template={node}'], stdout=PIPE)
        return p.communicate()[0].strip()

    def init(self):
        p = Popen(['hg', 'clone', self.url, self.name], stdout=PIPE)
        return p.communicate()[0].strip()

    def pull(self):
        p = Popen(['hg', '-R', self.name, 'pull'], stdout=PIPE)
        return p.communicate()[0].strip()

    def update(self, revision):
        if not revision:
            raise BundleError("invalid revision")

        p = Popen(['hg', '-R', self.name, 'update', '-r', revision])
        p.wait()

class GitBundle(Bundle):
    def __init__(self, *args, **kwargs):
        Bundle.__init__(self, *args, **kwargs)
        self.vcs = "git"

    def get_url(self):
        os.chdir(self.name)
        try:
            p = Popen(['git', 'config','remote.origin.url'], stdout=PIPE, shell=True)
            url = p.communicate()[0].strip()
        except Exception, e:
            raise BundleError(e)
        finally:
            os.chdir('..')

        return url

    def get_head(self):
        os.chdir(self.name)
        try:
            p = Popen(['git', 'log','-n1', 'HEAD', '--format=%H'], stdout=PIPE, shell=True)
            head = p.communicate()[0].strip()
        except Exception, e:
            raise BundleError(e)
        finally:
            os.chdir('..')

        return head

    def get_tip(self):
        os.chdir(self.name)
        try:
            p = Popen(['git', 'log','-n1', 'origin/master', '--format=%H'], stdout=PIPE, shell=True)
            tip = p.communicate()[0].strip()
        except Exception, e:
            raise BundleError(e)
        finally:
            os.chdir('..')

        return tip

    def init(self):
        p = Popen(['git', 'clone', self.url, self.name], stdout=PIPE)
        return p.communicate()[0].strip()

    def update(self, revision):
        if not revision:
            raise BundleError("invalid revision")

        os.chdir(self.name)
        try:
            p = Popen(['git', 'merge', '--ff-only', revision], shell=True)
            p.wait()
        except Exception, e:
            raise BundleError(e)
        finally:
            os.chdir('..')

        return result

    def pull(self):
        os.chdir(self.name)
        try:
            p = Popen(['git', 'fetch'], stdout=PIPE, shell=True)
            result = p.communicate()[0].strip()
        except Exception, e:
            raise BundleError(e)
        finally:
            os.chdir('..')

        return result
