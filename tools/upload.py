import argparse
import pathlib
import subprocess
import sys

from select_port import choose_port


PROJECT_DIR = pathlib.Path(__file__).resolve().parent.parent
SOURCE_DIR = PROJECT_DIR / "app"
SOURCE_ITEMS = (
    "boot.py",
    "main.py",
    "config.json",
    "connectivity",
    "hardware",
    "system",
)


def upload_app(port):
    sources = [str(SOURCE_DIR / item) for item in SOURCE_ITEMS]
    subprocess.run(
        [
            sys.executable,
            "-m",
            "mpremote",
            "connect",
            port,
            "fs",
            "cp",
            "-r",
            *sources,
            ":",
        ],
        cwd=PROJECT_DIR,
        check=True,
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port")
    args = parser.parse_args()

    port = args.port or choose_port()
    upload_app(port)


if __name__ == "__main__":
    main()
