# Find repeated lines

Read-only teaching tool for one UTF-8 text file. It counts exact strings, so
case and spaces matter. Blank lines have no characters and are labeled in the
report. Ties keep first-appearance order. Lines use Python str.splitlines
boundaries, not visual wrapping in an editor.

The report prints line contents: practise only on fictional or non-sensitive
data. It does not decide which copies to keep. An explicit file path can follow
a link to a target elsewhere. Link handling is unchanged and not tested here.

## Practise

Save all three files in a new empty lesson folder. Python 3 is required:

    python make_sample.py
    python dupelines.py sample/shopping.txt
    python -m unittest -v

Setup creates sample beside the script and refuses any existing sample path.
It never deletes or resets an old sample. Use a different new empty lesson
folder if it refuses. The shopping list is fictional practice text.

## Evidence

22 tests use temporary fixtures, including sample-count tests. They cover exact
string counting, CLI errors, unchanged source metadata, setup file/folder
collision refusal, original bytes, nested sentinel data and repeat-run
preservation. These small fixture passes are not universal safety proof.

Two GitHub-hosted Windows recordings and two Ubuntu recordings pass all tests.
The driver first saves the repeated-comparison version and records its repeated
reports, then saves the dictionary counter, as the lesson shows. Displayed
output uses first Windows output. Paired runs differ only in unittest elapsed
time; versions and test rendering can differ. No Windows desktop or macOS
session was tested.

## License

MIT (see LICENSE).
