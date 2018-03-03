import imp
import sys
import os
from os.path import expanduser, exists, abspath, join, dirname
from contextlib import contextmanager
import logging
import snake


log = logging.getLogger("snake.plugins")


# virtualenv may not exist, but we also may not need it if the user is just
# running scripts that have no dependencies outside of the stdlib
try:
    import virtualenv
except ImportError:
    virtualenv = None

try:
    import pip
except ImportError:
    pip = None

# let's use our virtualenv_wrapper home if we have one, else default to
# something sensible.  we'll use this to create our new virtualenvs for plugins
# that require them
WORKON_HOME = os.environ.get("WORKON_HOME", "~/.virtualenvs")
VENV_BASE_DIR = abspath(expanduser(WORKON_HOME))
BUNDLE_DIR = abspath(expanduser("~/.vim/bundle"))
IS_PY3 = sys.version_info[0] == 3


if IS_PY3:
    def execfile(name, ctx):
        exec(open(name).read(), ctx)


def venv_exists(plugin_name):
    return exists(join(VENV_BASE_DIR, plugin_name))

def pip_install(reqs_file, install_dir):
    """ takes a requirements file and installs all the reqs in that file into
    the virtualenv """
    args = ["install", "--quiet", "-t", install_dir, "-r", reqs_file]
    exit_code = pip.main(args)

    # we have to specify --system sometimes on ubuntu, because ubuntu can ship
    # with an older pip which defaults to --user, which conflicts with -t.
    # --system effectively disables --user (ugly workaround)
    if exit_code != 0:
        args.append("--system")
        pip.main(args)


def venv_name_from_module_name(name):
    return "snake_plugin_%s" % name

def new_venv(name):
    home_dir = join(VENV_BASE_DIR, name)
    virtualenv.create_environment(home_dir)
    return home_dir

def find_site_packages(venv_dir):
    return join(venv_dir, "lib", "python%s" % sys.version[:3], "site-packages")

class SnakePluginHook(object):
    """ allows us to import plugins while installing their dependencies like so:
        
        from snake.plugins import something

    if "requirements.txt" exists in the directory where the "something" module
    lives, they will be installed to the virtualenv for "something"

    https://www.python.org/dev/peps/pep-0302/
    """

    def __init__(self, plugin_paths):
        self.plugin_paths = plugin_paths

    def find_module(self, fullname, path=None):
        loader = None
        self.parts = fullname.split(".")
        self.plugin_module = ".".join(self.parts[-1:])

        if fullname.startswith("snake.plugins"):
            # its our initial snake_plugins dummy module
            if len(self.parts) == 2:
                loader = self

            # it's a plugin
            # notice we're checking for an exact match of 3 parts.  like
            # "snake.plugins.something".  if "something" is a package, we only
            # want to use our plugin hook for that top level module.  any
            # relative imports should be handled by the vanilla plugin system
            elif len(self.parts) == 3:
                # try to see if it actually is a snake plugin by searching the
                # plugin paths.  if we can't find it, we'll just end up
                # returning None for our loader
                try:
                    imp.find_module(self.plugin_module, self.plugin_paths)
                except ImportError:
                    pass
                # we found the plugin
                else:
                    loader = self

        return loader

    def load_module(self, fullname):
        mod = None

        # we haven't loaded it, so let's figure out what we're loading
        if fullname.startswith("snake.plugins"):

            # its our initial snake_plugins dummy module
            if len(self.parts) == 2:
                mod = imp.new_module(self.parts[0])

                mod.__name__ = "snake.plugins"
                mod.__loader__ = self
                mod.__file__ = "<snake.plugins>"
                mod.__path__ = self.plugin_paths
                mod.__package__ = fullname

            # it's a snake plugin
            elif len(self.parts) == 3:
                plugin_name = self.parts[-1]
                h, pathname, desc = imp.find_module(self.plugin_module,
                        self.plugin_paths)

                is_package = desc[-1] == imp.PKG_DIRECTORY

                # the module is a package, therefore there might be a
                # requirements file, and if there's a reqs file, there's a
                # virtualenv that we need to activate
                if is_package:
                    venv_name = venv_name_from_module_name(plugin_name)
                    reqs = join(pathname, "requirements.txt")

                    needs_venv = not venv_exists(venv_name) and exists(reqs)
                    can_make_venv = virtualenv is not None and pip is not None

                    # no virtualenv for this plugin?  but we have a requirements
                    # file?  create one and install all of the requirements
                    if needs_venv:
                        if can_make_venv:
                            print("Creating virtual environment %s for Snake \
plugin %s..." % (venv_name, plugin_name))
                            venv_dir = new_venv(venv_name)
                            print("Installing requirements for plugin %s..." %
                                    plugin_name)
                            pip_install(reqs, find_site_packages(venv_dir))
                        else:
                            raise Exception("Plugin %s requires a virtualenv. \
Please install virtualenv and pip so that one can be created." % plugin_name)

                    # we must have had requirements, because we've created a
                    # virtualenv.  go ahead and evaluate our module inside our new
                    # venv
                    if venv_exists(venv_name):
                        with in_virtualenv(venv_name):
                            mod = imp.load_module(fullname, h, pathname, desc)
                            mod.__virtualenv__ = venv_name

                    else:
                        mod = imp.load_module(fullname, h, pathname, desc)

                # we're not a package, there is no virtualenv, so load the
                # module as regular
                else:
                    mod = imp.load_module(fullname, h, pathname, desc)

                mod.__loader__ = self
                mod.__package__ = fullname
            sys.modules[fullname] = mod

        return mod


_snake_plugin_paths = [BUNDLE_DIR]
sys.meta_path.insert(0, SnakePluginHook(_snake_plugin_paths))



@contextmanager
def in_virtualenv(venv_name):
    """ activates a virtualenv for the context of the with-block """
    old_path = os.environ["PATH"]
    old_sys_path = sys.path[:]

    activate_this = join(VENV_BASE_DIR, venv_name, "bin/activate_this.py")
    execfile(activate_this, dict(__file__=activate_this))

    try:
        yield
    finally:
        os.environ["PATH"] = old_path
        sys.prefix = sys.real_prefix
        sys.path[:] = old_sys_path


def import_source(name, path):
    desc = (".py", "U", imp.PY_SOURCE)
    h = open(path, desc[1])
    module = imp.load_module(name, h, path, desc)
    return module


load_vimrc = bool(int(os.environ.get("LOAD_VIMPY", "1")))

vimrc_path = expanduser("~/.vimrc.py")
if exists(vimrc_path) and load_vimrc:
    import_source("vimrc", vimrc_path)
