"""make_sample.py - create a made-up practice file for the lesson.

Creates a folder called "sample" next to this script holding one
made-up shopping list with a few repeated lines. Run it again any
time; it first removes the old sample folder.
"""
import os
import shutil

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
    if os.path.isdir(SAMPLE):
        shutil.rmtree(SAMPLE)
    os.makedirs(SAMPLE)
    path = os.path.join(SAMPLE, "shopping.txt")
    with open(path, "w", newline="") as handle:
        handle.write(LIST)
    print("Sample folder ready: " + SAMPLE)
    print("It holds one made-up list, shopping.txt, with 14 lines.")


if __name__ == "__main__":
    main()
