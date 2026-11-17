import os


def get_release(self):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "version.txt")
    with open(path) as f:
        return f.read().strip()
