"""dupelines.py - find the repeated lines in a text file.

Read-only: it only looks. It never changes, moves or deletes anything.

Lines are split the way Python's str.splitlines() splits them. A
duplicate means the exact same text: letter case and spaces count, so
"Milk" and "milk" are different lines, and "Milk" and "Milk " are too.
Blank lines are lines with no characters at all and show as
"(blank line)". The file must be plain UTF-8 text.

Usage:
    python dupelines.py FILE
"""
import sys
import stat
from pathlib import Path


def safe_input(value, directory=False):
    path = Path(value).absolute()
    if '..' in path.parts:
        raise OSError('Parent-traversal paths are unsupported.')
    for part in [*reversed(path.parents), path]:
        info = part.lstat()
        if stat.S_ISLNK(info.st_mode) or getattr(info, 'st_file_attributes', 0) & 0x400:
            raise OSError('Links/reparse points are unsupported.')
    info = path.lstat()
    if directory:
        if not stat.S_ISDIR(info.st_mode):
            raise NotADirectoryError('Expected an ordinary directory.')
    elif not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        raise OSError('Expected an ordinary singly linked file.')
    return path







def count_kinds(lines):
    """Return a dict mapping each line to how many times it appears,
    in first-appearance order."""
    counts = {}
    for line in lines:
        counts[line] = counts.get(line, 0) + 1
    return counts


def repeated_rows(counts):
    """Return (line, times) rows for lines appearing more than once,
    most copies first; ties keep first-appearance order."""
    rows = [(line, times) for line, times in counts.items() if times > 1]
    rows.sort(key=lambda row: -row[1])
    return rows


def label(line):
    return line if line != "" else "(blank line)"


def main(argv):
    if len(argv) != 2 or argv[1] in ("-h", "--help"):
        print("Usage: python dupelines.py FILE", file=sys.stderr)
        return 2
    path = argv[1]
    try:
        with open(safe_input(path), "rb") as handle:
            data = handle.read()
    except OSError:
        print("No such file: " + path, file=sys.stderr)
        return 2
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        print("Not plain UTF-8 text: " + path, file=sys.stderr)
        return 1
    lines = text.splitlines()
    counts = count_kinds(lines)
    rows = repeated_rows(counts)
    print("Repeated lines")
    print("File: " + path)
    print()
    if rows:
        print("times  line")
        print("-----  ----")
        for line, times in rows:
            print("%5d  %s" % (times, label(line)))
        print()
    else:
        print("No repeated lines.")
        print()
    kinds = len(rows)
    if kinds == 0:
        tail = "no line is repeated"
    elif kinds == 1:
        tail = "1 kind of line is repeated"
    else:
        tail = "%d kinds of line are repeated" % kinds
    print("%d lines read, %d distinct; %s." % (len(lines), len(counts), tail))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
