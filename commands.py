from errors import BManError

class CommandError(BManError): pass

command_list = {}

def export(name_or_method=None):
    if callable(name_or_method):
        command_list[name_or_method.__name__] = name_or_method
        return name_or_method
    else:
        def real_decorator(func):
            command_list[name_or_method] = func
            return func

        return real_decorator

def execute(command, console, bundles, options, args):
    try:
        command_list[command](console, bundles, options, args)
    except KeyError:
        raise CommandError("No such command: %s" % (command))


@export("list")
def list_all(console, bundles, options, args):
    maxname = max(len(name) for name in bundles.keys())
    console.write_line("Listing all bundles:")
    for name, bundle in bundles.items():
        console.write("\t%s" % (name), "white")
        console.write(" " * (maxname - len(name) + 1))

        if not bundle.installed:
            console.write(" MISSING", "red")
        elif not bundle.tracked:
            console.write(" UNTRACKED", "red")
        else:
            if bundle.head != bundle.tip:
                console.write(" OUT-OF-DATE", "yellow")
            if bundle.head != bundle.saved_revision:
                console.write(" MODIFIED", "yellow")

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
            console.write_line("Adding bundle: %s" % (name))
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
                console.write_line("Removing bundle: %s" % (name))
            else:
                fd.write(line)


@export
def pull(console, bundles, options, args):
    if len(args) > 0:
        names = args
    else:
        names = bundles.keys()

    for name in names:
        bundle = bundles[name]

        if bundle.installed:
            console.write_line("Pulling bundle: %s" % (bundle.name))
            bundle.pull()


@export
def init(console, bundles, options, args):
    if len(args) > 0:
        names = args
    else:
        names = bundles.keys()

    for name in names:
        bundle = bundles[name]
        if bundle.tracked and not bundle.installed:
            console.write_line("Initializing bundle: %s" % (name))
            result = bundle.init()

            if options.verbose:
                console.write_line(result, color="yellow")
                console.write_line();
                console.write_line();
            options.revision = bundle.saved_revision
            update(console, bundles, options, args)
            


@export
def update(console, bundles, options, args):
    if len(args) > 0:
        names = args
    else:
        names = bundles.keys()

    for name in names:
        bundle = bundles[name]
        if options.revision:
            revision = options.revision
        else:
            revision = bundle.tip
        console.write_line("Updating bundle %s to revision %s" % (name, revision))

        result = bundle.update(revision)

        if options.verbose:
            console.write_line(result, color="yellow")
