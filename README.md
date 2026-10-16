# Repeated line finder

`dupelines.py` reads a plain text file and shows which lines appear
more than once, with counts, so you can tidy an exported list without
reading it line by line. It is read-only: it only looks, and it never
changes, moves or deletes anything. Run it first on the made-up
`sample` folder from `make_sample.py` before pointing it anywhere
else.

- A duplicate means the exact same text: letter case and spaces
  count. Blank lines show as `(blank line)`.
- The most repeated lines come first; ties keep file order.
- The file must be plain UTF-8 text. Windows (CRLF), Mac/Linux (LF)
  and old Mac (CR) endings all count, and a last line without an
  ending still counts.

## Use

    python make_sample.py
    python dupelines.py sample/shopping.txt
    python dupelines.py "C:\Users\you\Documents\my-list.txt"

## Tests

    python -m unittest -v

Works on Windows, Mac and Linux with Python 3.10 or newer. Nothing to
install: it uses only what comes with Python.

## License

MIT (see LICENSE).
