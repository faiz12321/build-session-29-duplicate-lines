"""make_sample.py - create a made-up practice file for the lesson.

Creates a folder called "sample" next to this script holding one
made-up shopping list with a few repeated lines. It refuses any existing sample
path before writing. Nothing is deleted or replaced.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SAMPLE = os.path.join(HERE, "sample")

LIST = """Milk
Bread
Eggs
Milk
Cheese
Bread
Apples
Milk
Yogurt

Rice
Pasta

Tea
"""


def main():
    try:
        os.mkdir(SAMPLE)
    except FileExistsError:
        raise SystemExit("Stopped: sample already exists. Nothing was replaced or deleted.")
    path = os.path.join(SAMPLE, "shopping.txt")
    with open(path, "x", encoding="utf-8", newline="") as handle:
        handle.write(LIST)
    print("Created a new sample folder beside make_sample.py.")
    print("It holds one made-up list, shopping.txt, with 14 lines.")


if __name__ == "__main__":
    main()
