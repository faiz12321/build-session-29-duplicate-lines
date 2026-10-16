# Report repeated fictional text lines

Save three source files in a NEW empty lesson folder.

    python make_sample.py
    python dupelines.py sample/shopping.txt
    python -m unittest -v

Two Windows and two Ubuntu full replays run exact visible source versions. Final 35 small fixture tests pass (Unix pipe skips on Windows); symlink creation can skip where unavailable. Displayed stdout is first Windows output, not normalized or mixed. Pair differences are unittest time.
Only link/error changes: refuse input/ancestor symbolic links/reparse points, hardlinks, special files and traversal before reading. Read/metadata errors remain exit 2 with the original brief error wording. Setup refuses linked parents/traversal and existing sample paths, without reset or deletion. Naive first version remains fictional-sample-only and must be replaced.
Original UTF-8 decoding, splitlines, exact case/space duplicate matching, blank-line label, occurrence sorting and first-appearance ties remain unchanged. Exit 0 remains a successful report whether repeated lines exist or not; invalid UTF-8 stays exit 1, usage/read errors 2. No deduplication, rewriting, whitespace normalization or data-safety claim.
The checker has no write/move/delete/network code but reads the whole file and stores line counts in memory. No size/time/resource limit, atomic snapshot or hostile-race defense. Stop editors/sync. Repeated-line output exposes file contents and can contain secrets; keep private output private. Small fictional fixtures are not proof on every filesystem. No desktop Windows/macOS recording. Recorder removes only its own temporary fixture folder. Decisions and feedback are teaching text, not recorded output.

MIT code. Python separately licensed/not included.

Reference: https://docs.python.org/3/library/os.html

Windows pair: https://github.com/faiz12321/lesson-lab/actions/runs/38976673971
Ubuntu pair: https://github.com/faiz12321/lesson-lab/actions/runs/38976747036
