import argparse
import pathlib
import subprocess
import sys

from select_port import choose_port


PROJECT_DIR = pathlib.Path(__file__).resolve().parent.parent


def run_app(port):
    subprocess.run(
        [
            sys.executable,
            "-m",
            "mpremote",
            "connect",
            port,
            "exec",
            "exec(open('main.py').read())",
        ],
        cwd=PROJECT_DIR,
        check=True,
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port")
    args = parser.parse_args()

    port = args.port or choose_port()
    run_app(port)


if __name__ == "__main__":
    main()
