"""Tests for dupelines.py. They run in a temporary folder, so real
files are never touched."""
import contextlib
import io
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

import dupelines

HERE = os.path.dirname(os.path.abspath(__file__))


def run_main(args):
    out = io.StringIO()
    err = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = dupelines.main(args)
    return rc, out.getvalue(), err.getvalue()


class CountTests(unittest.TestCase):
    def test_basic_counts(self):
        self.assertEqual(dupelines.count_kinds(["a", "b", "a"]), {"a": 2, "b": 1})

    def test_first_appearance_order(self):
        self.assertEqual(list(dupelines.count_kinds(["b", "a", "b"])), ["b", "a"])

    def test_case_sensitive(self):
        self.assertEqual(dupelines.count_kinds(["Milk", "milk"]), {"Milk": 1, "milk": 1})

    def test_spaces_count(self):
        self.assertEqual(dupelines.count_kinds(["a", "a "]), {"a": 1, "a ": 1})


class RowTests(unittest.TestCase):
    def test_only_repeated_lines(self):
        rows = dupelines.repeated_rows({"a": 2, "b": 1, "c": 3})
        self.assertEqual(rows, [("c", 3), ("a", 2)])

    def test_most_copies_first_ties_in_order(self):
        rows = dupelines.repeated_rows({"x": 2, "y": 5, "z": 2})
        self.assertEqual(rows, [("y", 5), ("x", 2), ("z", 2)])

    def test_no_repeats(self):
        self.assertEqual(dupelines.repeated_rows({"a": 1, "b": 1}), [])

    def test_blank_line_label(self):
        self.assertEqual(dupelines.label(""), "(blank line)")
        self.assertEqual(dupelines.label("x"), "x")


class Base(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    def write(self, name, data):
        path = os.path.join(self.dir, name)
        with open(path, "wb") as handle:
            handle.write(data)
        return path


class MainTests(Base):
    def test_report_shape(self):
        path = self.write("list.txt", b"a\nb\na\n")
        rc, out, _ = run_main(["dupelines.py", path])
        self.assertEqual(rc, 0)
        self.assertIn("    2  a", out)
        self.assertIn("3 lines read, 2 distinct; 1 kind of line is repeated.", out)

    def test_no_repeats_message(self):
        path = self.write("list.txt", b"a\nb\nc\n")
        rc, out, _ = run_main(["dupelines.py", path])
        self.assertEqual(rc, 0)
        self.assertIn("No repeated lines.", out)
        self.assertIn("no line is repeated.", out)

    def test_blank_lines_reported(self):
        path = self.write("list.txt", b"a\n\n\n")
        rc, out, _ = run_main(["dupelines.py", path])
        self.assertEqual(rc, 0)
        self.assertIn("    2  (blank line)", out)

    def test_crlf_and_last_line_without_ending(self):
        path = self.write("list.txt", b"a\r\nb\r\na")
        rc, out, _ = run_main(["dupelines.py", path])
        self.assertEqual(rc, 0)
        self.assertIn("    2  a", out)
        self.assertIn("3 lines read", out)

    def test_empty_file(self):
        path = self.write("list.txt", b"")
        rc, out, _ = run_main(["dupelines.py", path])
        self.assertEqual(rc, 0)
        self.assertIn("0 lines read, 0 distinct", out)

    def test_not_utf8(self):
        path = self.write("odd.txt", b"\xff\xfe not text")
        rc, _, err = run_main(["dupelines.py", path])
        self.assertEqual(rc, 1)
        self.assertIn("Not plain UTF-8 text", err)

    def test_missing_file(self):
        rc, _, err = run_main(["dupelines.py", os.path.join(self.dir, "nope.txt")])
        self.assertEqual(rc, 2)
        self.assertIn("No such file", err)

    def test_usage_error(self):
        rc, _, err = run_main(["dupelines.py"])
        self.assertEqual(rc, 2)
        self.assertIn("Usage", err)

    def test_run_leaves_file_unchanged(self):
        path = self.write("list.txt", b"a\nb\na\n")
        before = (os.path.getsize(path), os.path.getmtime(path),
                  sorted(os.listdir(self.dir)))
        rc, _, _ = run_main(["dupelines.py", path])
        self.assertEqual(rc, 0)
        after = (os.path.getsize(path), os.path.getmtime(path),
                 sorted(os.listdir(self.dir)))
        self.assertEqual(before, after)


class SampleTests(unittest.TestCase):
    def test_sample_counts(self):
        subprocess.run([sys.executable, os.path.join(HERE, "make_sample.py")],
                       check=True, capture_output=True)
        rc, out, _ = run_main(["dupelines.py", os.path.join(HERE, "sample", "shopping.txt")])
        self.assertEqual(rc, 0)
        self.assertIn("    3  Milk", out)
        self.assertIn("    2  Bread", out)
        self.assertIn("    2  (blank line)", out)
        self.assertIn("14 lines read, 10 distinct; 3 kinds of line are repeated.", out)

    def test_source_is_read_only(self):
        with open(os.path.join(HERE, "dupelines.py"), "r") as handle:
            source = handle.read()
        self.assertIn('open(path, "rb")', source)
        for word in ("os.remove", "os.unlink", "os.rename", "os.replace",
                     "os.mkdir", "os.rmdir", "shutil", ".write(", "writelines",
                     '"w")', "'w')", '"a")', "'a')"):
            self.assertNotIn(word, source)


if __name__ == "__main__":
    unittest.main()
