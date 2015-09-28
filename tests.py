import os
from os.path import join, dirname, abspath, exists
import tempfile
import sys
import unittest
import sh
import pickle
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
let mapleader = ","
set clipboard=unnamed
python << EOF
import sys
from os.path import expanduser
sys.path.insert(0, "{SNAKE_DIR}")
import snake
""".format(SNAKE_DIR=SNAKE_DIR))


def run_vim(script, input_str=None, vimrc=VIMRC.name, commands=None):
    # we can't use a real fifo because it will block on opening, because one
    # side will wait for the other side to open before unblocking
    fifo = tempfile.NamedTemporaryFile(delete=True)

    # we do some super ugly stuff and wrap our script in some helpers, namely a
    # helper to send output from our snake script to our test
    script = """python << EOF
import pickle
from snake import *
def send(stuff):
    with open("{fifo_filename}", "w") as output:
        pickle.dump(stuff, output)
{script}
EOF
    """.format(script=script, fifo_filename=fifo.name)
    script_file = create_tmp_file(script)
    input_file = create_tmp_file(input_str or "")

    # use our custom vimrc, use binary mode (dont add newlines automatically),
    # and load script_file as our script to run
    args = ["-N", "-n", "-i", "NONE", "-u", vimrc, "-S", script_file.name, "-b"]

    #commands.append("exec 'silent !echo '. errmsg")

    # sometimes we need to specify our own commands, but most times not
    if commands is None:
        # save and exit
        commands = ["wqa!"]

    for command in commands:
        args.extend(["-c", command])
    args.append(input_file.name)

    env = os.environ.copy()
    env["LOAD_VIMPY"] = "0"
    p = sh.vim(*args, _tty_in=True, _env=env)
    #err = clean_output(p.stdout.decode("ascii"))
    output = p.stdout

    input_file.seek(0)
    changed = input_file.read().decode("utf8")

    sent_data = fifo.read()
    if sent_data:
        output = pickle.loads(sent_data)
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


    def test_delete_word(self):
        script = r"""
keys("^5w")
delete_word()
"""
        changed, output = run_vim(script, self.sample_text)
        self.assertEqual(changed, "The quick brown fox jumps  the lazy dog")


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


    def test_num_lines(self):
        script = r"""
send(get_num_lines())
"""
        _, output = run_vim(script, self.sample_block)
        self.assertEqual(output, 8)

    def test_last_line(self):
        script = r"""
keys("gg")
test1 = is_last_line()
keys("G")
test2 = is_last_line()
send([test1, test2])
"""
        _, output = run_vim(script, self.sample_block)
        self.assertFalse(output[0])
        self.assertTrue(output[1])

    def test_preserve_cursor(self):
        script = r"""
keys("gg^w")
with preserve_cursor():
    keys("jj^w")
    word1 = get_word()

word2 = get_word()
send([word1, word2])
"""
        _, output = run_vim(script, self.sample_block)
        self.assertEqual(output[0], "art")
        self.assertEqual(output[1], "Mary")

    def test_search(self):
        script = r"""
search("Mary")
word1 = get_word()
pos1 = get_cursor_position()

search("Mary")
word2 = get_word()
pos2 = get_cursor_position()

send([(word1, pos1), (word2, pos2)])
"""
        _, output = run_vim(script, self.sample_block)
        self.assertEqual(output, [("Mary", (1, 6)), ("Mary", (5, 6))])


    def test_filetype(self):
        script = r"""
called = 0
@when_buffer_is("text")
def hooks(ctx):
    global called
    called += 1

count1 = called
set_option("filetype", "python")
count2 = called
set_option("filetype", "text")
count3 = called

send([count1, count2, count3])
"""
        _, output = run_vim(script, self.sample_text)
        self.assertEqual(output, [0, 0, 1])


    def test_current_file(self):
        script = r"""
send(get_current_file())
"""
        _, output = run_vim(script)
        self.assertEqual(tempfile.gettempdir(), dirname(output))


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
        self.assertEqual(output, [(1,1), (2,3)])


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
    def test_leader(self):
        script = r"""
def side_effect():
    send(True)

key_map("<leader>a", side_effect)
keys("\<leader>a")
"""
        changed, output = run_vim(script)
        self.assertTrue(output)

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
    return "really fast"

visual_key_map("a", process)
keys("Wviwa")
"""
        changed, output = run_vim(script, self.sample_text)
        self.assertEqual(output, "quick")
        self.assertEqual(changed, "The really fast brown fox jumps over the lazy dog")



class OptionsTests(VimTests):
    def test_get_set_value(self):
        script = r"""
o1 = int(get_option("tw"))
set_option("tw", 80)
o2 = int(get_option("tw"))
send([o1, o2])
"""
        _, output = run_vim(script)
        self.assertEqual(output, [0, 80])

    def test_get_set_flag(self):
        script = r"""
o1 = int(get_option("tw"))
set_option("tw", 80)
o2 = int(get_option("tw"))
send([o1, o2])
"""
        _, output = run_vim(script)
        self.assertEqual(output, [0, 80])


class VariableTests(VimTests):
    def test_let(self):
        script = r"""
var_name = "some_var"
orig = get(var_name)
let(var_name, "testing")
new = get(var_name)
send({
    "original": orig,
    "new": new,
})
"""
        _, output = run_vim(script)
        self.assertEqual(output["original"], None)
        self.assertEqual(output["new"], "testing")


    def test_multi_let(self):
        script = r"""
multi_let(
    "test",
    a="1",
    b="2",
    c="3"
)
send({
    "a": get("a", "test"),
    "b": get("b", "test"),
    "c": get("c", "test"),
})
"""
        _, output = run_vim(script)
        self.assertEqual(output["a"], "1")
        self.assertEqual(output["b"], "2")
        self.assertEqual(output["c"], "3")


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



class BufferTests(VimTests):
    def test_new_buffer(self):
        script = r"""
buf1 = get_current_buffer()
num1 = get_num_buffers()
n = new_buffer("test")
buf2 = get_current_buffer()
num2 = get_num_buffers()
set_buffer(n)
buf3 = get_current_buffer()
send([buf1, num1, buf2, num2, buf3])
"""
        changed, output = run_vim(script, self.sample_text, commands=["qa!"])
        self.assertEqual(output, [1, 1, 1, 2, 2])

    def test_get_buffers(self):
        script = r"""
new_buffer("test1")
new_buffer("test2")
send(get_buffers())
"""
        changed, output = run_vim(script, self.sample_text, commands=["qa!"])
        del output[1]["name"]
        self.assertDictEqual(output, {
            1: {'flags': {'active': True,
                'alternate': False,
                'current': True,
                'errors': False,
                'hidden': False,
                'modified': False,
                'readonly': False,
                'unlisted': False},
                },
            2: {'flags': {'active': False,
                'alternate': False,
                'current': False,
                'errors': False,
                'hidden': True,
                'modified': False,
                'readonly': False,
                'unlisted': False},
                'name': 'test1'},
            3: {'flags': {'active': False,
                'alternate': True,
                'current': False,
                'errors': False,
                'hidden': True,
                'modified': False,
                'readonly': False,
                'unlisted': False},
                'name': 'test2'}
        })


class Opfunctests(VimTests):
    def test_opfunc_decorator(self):
        script = r"""
called = 0
@opfunc("t")
def side_effect(s):
    global called
    called += 1
keys("tw")
keys("tj")
send(called)
"""
        changed, output = run_vim(script)
        self.assertEqual(output, 3)

    def test_opfunc_motion(self):
        script = r"""
def process(stuff):
    send(stuff)
    return "really fast"

opfunc("t", process)
keys("Wt2W")
"""
        changed, output = run_vim(script, self.sample_text)
        self.assertEqual(output, "quick brown")
        self.assertEqual(changed, "The really fast fox jumps over the lazy dog")

if __name__ == "__main__":
    print(sh.vim(version=True))
    unittest.main(verbosity=2)
