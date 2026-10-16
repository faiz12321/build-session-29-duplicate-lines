from unittest import mock
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
from pathlib import Path

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
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.work = self.temp.name
        shutil.copyfile(os.path.join(HERE, "make_sample.py"),
                        os.path.join(self.work, "make_sample.py"))

    def setup_run(self):
        return subprocess.run([sys.executable, os.path.join(self.work, "make_sample.py")],
                              capture_output=True, text=True)

    def test_sample_counts(self):
        self.assertEqual(self.setup_run().returncode, 0)
        rc, out, _ = run_main(["dupelines.py", os.path.join(self.work, "sample", "shopping.txt")])
        self.assertEqual(rc, 0)
        self.assertIn("    3  Milk", out)
        self.assertIn("    2  Bread", out)
        self.assertIn("    2  (blank line)", out)
        self.assertIn("14 lines read, 10 distinct; 3 kinds of line are repeated.", out)

    def snapshot(self, root):
        return sorted((str(p.relative_to(root)), p.is_dir(), p.stat().st_size,
                       p.stat().st_mtime_ns, p.read_bytes() if p.is_file() else None)
                      for p in Path(root).rglob("*"))

    def test_setup_refuses_existing_folder_without_change(self):
        sample = Path(self.work) / "sample"
        (sample / "unrelated").mkdir(parents=True)
        (sample / "shopping.txt").write_bytes(b"ORIGINAL")
        (sample / "unrelated" / "deep.txt").write_bytes(b"KEEP")
        before = self.snapshot(sample)
        result = self.setup_run()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Nothing was replaced or deleted", result.stderr)
        self.assertEqual(before, self.snapshot(sample))

    def test_setup_refuses_existing_file(self):
        sample = Path(self.work) / "sample"
        sample.write_bytes(b"ORIGINAL")
        before = (sample.read_bytes(), sample.stat().st_mtime_ns)
        self.assertNotEqual(self.setup_run().returncode, 0)
        self.assertEqual(before, (sample.read_bytes(), sample.stat().st_mtime_ns))

    def test_rerun_preserves_generated_folder_and_user_file(self):
        self.assertEqual(self.setup_run().returncode, 0)
        sample = Path(self.work) / "sample"
        (sample / "user.txt").write_bytes(b"KEEP")
        before = self.snapshot(sample)
        self.assertNotEqual(self.setup_run().returncode, 0)
        self.assertEqual(before, self.snapshot(sample))

    def test_source_is_read_only(self):
        with open(os.path.join(HERE, "dupelines.py"), "r") as handle:
            source = handle.read()
        self.assertIn('open(safe_input(path), "rb")', source)
        for word in ("os.remove", "os.unlink", "os.rename", "os.replace",
                     "os.mkdir", "os.rmdir", "shutil", ".write(", "writelines",
                     '"w")', "'w')", '"a")', "'a')"):
            self.assertNotIn(word, source)


class PathSafety(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.base=Path(self.tmp.name);self.root=self.base/'tree';self.root.mkdir()
        self.file=self.root/'zero';self.file.write_bytes(b'')
    def link(self,path,target,directory=False):
        try:path.symlink_to(target,target_is_directory=directory)
        except OSError:self.skipTest('Symlinks unavailable')
    def code(self,path):
        with contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(io.StringIO()):
            return dupelines.main(['p',str(path)])
    def test_root_alias_refuses(self):
        p=self.base/'alias';self.link(p,self.root,True);self.assertEqual(self.code(p),2)
    def test_ancestor_alias_refuses(self):
        p=self.base/'alias';self.link(p,self.base,True);self.assertEqual(self.code(p/'tree'),2)
    def test_file_alias_refuses(self):
        p=self.base/'linked';self.link(p,self.file);self.assertEqual(self.code(p),2)
    def test_file_hardlink_refuses(self):
        p=self.base/'hard';os.link(self.file,p);self.assertEqual(self.code(p),2)
    def test_file_pipe_refuses(self):
        if not hasattr(os,'mkfifo'):self.skipTest('Unix pipe unavailable')
        p=self.base/'pipe';os.mkfifo(p);self.assertEqual(self.code(p),2)
    def test_file_self_loop_refuses(self):
        p=self.base/'loop';self.link(p,p);self.assertEqual(self.code(p),2)
    def test_file_dangling_refuses(self):
        p=self.base/'alias';self.link(p,self.base/'missing');self.assertEqual(self.code(p),2)
    def test_file_traversal_refuses(self):self.assertEqual(self.code(self.root/'..'/'tree'/'zero'),2)
    def test_file_ancestor_refuses(self):
        p=self.base/'alias';self.link(p,self.root,True);self.assertEqual(self.code(p/'zero'),2)
    def test_metadata_error_refuses(self):
        with mock.patch.object(Path,'lstat',side_effect=OSError('forced')):self.assertEqual(self.code(self.file),2)
    def test_reparse_attribute_refuses(self):
        real=Path.lstat
        def fake(p,*a,**kw):
            value=real(p,*a,**kw)
            if p==self.file:return type('Reparse',(),{'st_mode':value.st_mode,'st_file_attributes':0x400})()
            return value
        with mock.patch.object(Path,'lstat',fake):self.assertEqual(self.code(self.file),2)
    def test_setup_alias_parent_refuses(self):
        import make_sample
        p=self.base/'alias';self.link(p,self.root,True)
        with mock.patch.object(make_sample,'SAMPLE',str(p/'new')):
            with self.assertRaises(OSError):make_sample.main()
        self.assertFalse((self.root/'new').exists())
    def test_setup_traversal_refuses(self):
        import make_sample
        with mock.patch.object(make_sample,'SAMPLE',str(self.root/'..'/'new')):
            with self.assertRaises(OSError):make_sample.main()



if __name__ == "__main__":
    unittest.main()
