from sys import stdout

class Console(object):
    def write(self, text="", color=None):
        self.save_color()
        self.set_color(color)
        stdout.write(text)
        self.restore_color()

    def write_line(self, text="", color=None):
        self.save_color()
        self.set_color(color)
        stdout.write("%s\n" % (text))
        self.restore_color()

    def set_color(self, color=None):
        pass

    def save_color(self):
        pass

    def restore_color(self):
        pass
