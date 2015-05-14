import os
from os.path import join, dirname, abspath, exists
import tempfile
import sys
import unittest
import sh
import json
import codecs
import re

THIS_DIR = dirname(abspath(__file__))
SNAKE_DIR = join(THIS_DIR, "plugin")
IS_PY3 = sys.version_info[0] == 3

def create_tmp_file(code, prefix="tmp", delete=True):
    """ creates a temporary test file that lives on disk, on which we can run
    python with sh """

    py = tempfile.NamedTemporaryFile(prefix=prefix, delete=delete)
    if IS_PY3:
        code = bytes(code, "UTF-8")
    py.write(code)
    py.flush()
    # we don't explicitly close, because close will remove the file, and we
    # don't want that until the test case is done.  so we let the gc close it
    # when it goes out of scope
    return py


def clean_output(output):
    """ for some reason, vim is outputting escape sequences in our errors.  we
    need to trim it out so we can read the errors """
    return re.sub(r'\x1b[^m]*m', '', output)

VIMRC = create_tmp_file(r"""
python << EOF
import sys
from os.path import expanduser
sys.path.insert(0, "{SNAKE_DIR}")
import snake
""".format(SNAKE_DIR=SNAKE_DIR))


def run_vim(script, input_str=None, vimrc=VIMRC.name):
    # we can't use a real fifo because it will block on opening, because one
    # side will wait for the other side to open before unblocking
    fifo = tempfile.NamedTemporaryFile(delete=True)

    # we do some super ugly stuff and wrap our script in some helpers, namely a
    # helper to send output from our snake script to our test
    script = """python << EOF
import json
from snake import *
output = open("{fifo_filename}", "w")
def send(stuff):
    output.write(json.dumps(stuff))
    output.flush()
{script}
output.close()
EOF
    """.format(script=script, fifo_filename=fifo.name)
    script_file = create_tmp_file(script)
    input_file = create_tmp_file(input_str or "")
    commands = []

    # use our custom vimrc, use binary mode (dont add newlines automatically),
    # and load script_file as our script to run
    args = ["-N", "-n", "-i", "NONE", "-u", vimrc, "-S", script_file.name, "-b"]

    #commands.append("exec 'silent !echo '. errmsg")
    # force quit after our script runs
    commands.append("wq!")

    for command in commands:
        args.extend(["-c", command])
    args.append(input_file.name)

    p = sh.vim(*args, _tty_in=True)
    #err = clean_output(p.stdout.decode("ascii"))
    output = p.stdout

    input_file.seek(0)
    changed = input_file.read().decode("utf8")

    sent_data = fifo.read().decode("utf8")
    if sent_data:
        output = json.loads(sent_data)
    else:
        output = None
    return changed, output


class VimTests(unittest.TestCase):
    def setUp(self):
        self.sample_text = "The quick brown fox jumps over the lazy dog"
        self.sample_block = """
Hail Mary, full of grace.
The Lord is with thee.
Blessed art thou amongst women,
and blessed is the fruit of thy womb, Jesus.
Holy Mary, Mother of God,
pray for us sinners,
now and at the hour of our death.
Amen.
""".strip()


class Tests(VimTests):

    def test_replace_word(self):
        script = """
replace_word("Test")
keys("3w")
replace_word("awesome")
"""

        changed, output = run_vim(script, self.sample_text)
        self.assertEqual(changed, "Test quick brown awesome jumps over the lazy dog")

    def test_get_word(self):
        script = r"""
keys("^5w")
over = get_word()
send(over)
"""

        changed, output = run_vim(script, self.sample_text)
        self.assertEqual(output, "over")

    def test_set_buffer_contents(self):
        script = r"""
buf = get_current_buffer()
set_buffer_contents(buf, "new stuff")
"""

        changed, output = run_vim(script, self.sample_text)
        self.assertEqual(changed, "new stuff")

    def test_abbrev(self):
        script = r"""
abbrev("abc", "123")
keys("iabc\<C-]>")
"""
        changed, output = run_vim(script)
        self.assertEqual(changed, "123\n")

    def test_abbrev_fn(self):
        script = r"""
def create_inc():
    i = [0]
    def inc():
        i[0] += 1
        return i[0]
    return inc

abbrev("abc", create_inc())
keys("iabc\<C-]> abc\<C-]>")
"""
        changed, output = run_vim(script)
        self.assertEqual(changed, "1 2\n")


class VisualTests(VimTests):
    def test_cursor_position(self):
        script = r"""
data = []

keys("gg^")
data.append(get_cursor_position())

keys("llj")
data.append(get_cursor_position())

send(data)
"""
        changed, output = run_vim(script, self.sample_block)
        self.assertEqual(output, [[1,1], [2,3]])


    def test_cursor_set_pos(self):
        script = r"""
keys("gg^l")
p1 = get_cursor_position()
keys("G$")
eof = get_cursor_position()

set_cursor_position(p1)
p2 = get_cursor_position()
send(p1 == p2 and p1 != eof)
"""

        changed, output = run_vim(script, self.sample_block)
        self.assertTrue(output)


    def test_get_visual_range(self):
        script = r"""
keys("ggllvjjl")
pos = get_visual_range()
send(pos)
"""
        changed, output = run_vim(script, self.sample_block)
        (start_row, start_col), (end_row, end_col) = output
        self.assertEqual(start_row, 1)
        self.assertEqual(start_col, 3)
        self.assertEqual(end_row, 3)
        self.assertEqual(end_col, 4)

    def test_get_visual_selection(self):
        script = r"""
keys("ggllvjjl")
send(get_visual_selection())
"""
        changed, output = run_vim(script, self.sample_block)
        self.assertEqual(output, "il Mary, full of grace.\nThe Lord is with \
thee.\nBles")

    def test_replace_visual_selection(self):
        script = r"""
keys("wwvee")
replace_visual_selection("awesome dude")
"""
        changed, output = run_vim(script, self.sample_text)
        self.assertEqual(changed, "The quick awesome dude jumps over the lazy \
dog")



class KeyMapTests(VimTests):
    def test_key_map_fn(self):
        script = r"""
called = 0
def side_effect():
    global called
    called += 1

key_map("a", side_effect)
keys("aaa")
send(called)
"""
        changed, output = run_vim(script)
        self.assertEqual(output, 3)

    def test_key_map_decorator(self):
        script = r"""
called = 0
@key_map("a")
def side_effect():
    global called
    called += 1

keys("aaaa")
send(called)
"""
        changed, output = run_vim(script)
        self.assertEqual(output, 4)

    def test_visual_key_map(self):
        script = r"""
def process(stuff):
    send(stuff)

visual_key_map("a", process)
keys("Wviewa")
"""
        changed, output = run_vim(script, self.sample_text)
        import pdb; pdb.set_trace() 


class RegisterTests(VimTests):
    def test_get_set_register(self):
        script = r"""
original = get_register("a")
set_register("a", "register a is set")
set_register("b", "register b is set")
new = get_register("a")
send({
    "original": original,
    "new": new,
})
"""
        _, output = run_vim(script)
        self.assertEqual(output["original"], None)
        self.assertEqual(output["new"], "register a is set")

    def test_clear_registers(self):
        script = r"""
set_register("a", "register a is set")
set_register("b", "register b is set")
set_register("c", "register c is set")
a = get_register("a")
b = get_register("b")
c = get_register("c")
clear_register("a")
clear_register("b")
new_a = get_register("a")
new_b = get_register("b")
new_c = get_register("c")
send({
    "a": a,
    "b": b,
    "c": c,
    "new_a": new_a,
    "new_b": new_b,
    "new_c": new_c,
})
"""
        _, output = run_vim(script)
        self.assertEqual(output["a"], "register a is set")
        self.assertEqual(output["b"], "register b is set")
        self.assertEqual(output["c"], "register c is set")

        self.assertEqual(output["new_a"], None)
        self.assertEqual(output["new_b"], None)
        self.assertEqual(output["new_c"], "register c is set")

    def test_preserve_registers(self):
        script = r"""
data = {}

with preserve_registers("a"):
    set_register("a", "123")

data["preserved_a"] = get_register("a")

set_register("a", "not preserved")
set_register("b", "i'll be preserved tho")
with preserve_registers("b"):
    set_register("a", "123")
    set_register("b", "456")

data["not_preserved_a"] = get_register("a")
data["preserved_b"] = get_register("b")
send(data)
"""

        _, output = run_vim(script)
        self.assertEqual(output["preserved_a"], None)
        self.assertEqual(output["not_preserved_a"], "123")
        self.assertEqual(output["preserved_b"], "i'll be preserved tho")
