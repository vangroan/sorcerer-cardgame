from contextlib import contextmanager
from enum import Enum
from argparse import ArgumentParser
import subprocess
import os, sys
from pathlib import Path


BACKEND = "backend"


class Cmd(Enum):
    SERVE = "serve"

    def __str__(self) -> str:
        return str(self.value)


@contextmanager
def chdir(file_path):
    olddir = os.curdir
    try:
        os.chdir(file_path)
        yield os.curdir
    finally:
        os.chdir(olddir)


def serve():
    backend_path = Path(__file__).parent / BACKEND
    python_path = sys.executable
    with chdir(backend_path):
        server_path = backend_path / "sorcerer" / "server.py"
        exit_code = subprocess.call([python_path, server_path])
        exit(exit_code)


def parse_args():
    parser = ArgumentParser()
    subparsers = parser.add_subparsers(dest="cmd")

    serve_cmd = subparsers.add_parser("serve")

    return parser.parse_args()


def main():
    args = parse_args()

    if args.cmd == Cmd.SERVE.value:
        serve()


if __name__ == "__main__":
    main()
