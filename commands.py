from errors import BManError

class CommandError(BManError): pass

command_list = {}

def export(func, name=None):
    if not name:
        name = func.__name__

    command_list[name] = func
    return func

def execute(command, console, bundles, options, args):
    try:
        command_list[command](console, bundles, options, args)
    except KeyError:
        raise CommandError("No such command: %s" % (command))


@export
def list_all(console, bundles, options, args):
    console.write_line("Listing all bundles:")
    for name, bundle in bundles.items():
        console.write("\t%s" % (name), "white")

        if not bundle.installed:
            console.write(" MISSING", "red")

        if not bundle.tracked:
            console.write(" UNTRACKED", "red")

        console.write_line()


@export
def tracked(console, bundles, options, args):
    console.write_line("Tracked bundles:")
    for name, bundle in bundles.items():
        if bundle.tracked:
            console.write("\t%s" % (name), "white")

        if not bundle.installed:
            console.write(" MISSING", "red")

        console.write_line()


@export
def heads(console, bundles, options, args):
    maxname = max(len(name) for name in bundles.keys())
    for name, bundle in bundles.items():
        console.write("%s" % (name), "white")
        if bundle.tracked:
            console.write("* ")
        else:
            console.write("  ")
        console.write(" "*(maxname - len(name)))
        console.write("%s " % (bundle.head), "yellow")
        console.write("\n")


@export
def detail(console, bundles, options, args):
    maxname = max(len(name) for name in bundles.keys())
    for name, bundle in bundles.items():
        console.write("%s" % (name), "white")
        if bundle.tracked:
            console.write("* ")
        else:
            console.write("  ")
        console.write(" "*(maxname - len(name)))
        console.write("%s " % (bundle.head), "yellow")
        console.write("%s " % (bundle.url), "magenta")
        console.write("\n")


@export
def urls(console, bundles, options, args):
    maxname = max(len(name) for name in bundles.keys())
    for name, bundle in bundles.items():
        console.write("%s" % (name), "white")
        if bundle.tracked:
            console.write("* ")
        else:
            console.write("  ")
        console.write(" "*(maxname - len(name)))
        console.write("%s " % (bundle.url), "magenta")
        console.write("\n")


@export
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


@export
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


@export
def pull(console, bundles, options, args):
    if len(args) > 0:
        names = args
    else:
        names = bundles.names

    for name in names:
        bundle = bundles[name]

        if bundle.installed:
            console.write_line("Pulling bundle: %s" % (bundle.name))
            bundle.pull()


@export
def update(console, bundles, options, args):
    pass


@export
def init(console, bundles, options, args):
    pass
