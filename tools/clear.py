import argparse
import pathlib
import subprocess
import sys

from select_port import choose_port


PROJECT_DIR = pathlib.Path(__file__).resolve().parent.parent


def confirm_clear(port, yes):
    print("[host] port: {}".format(port))
    print("[host] target: device filesystem root")
    print("[host] command: mpremote fs rm -r :")
    if yes:
        return

    answer = input("[host] type CLEAR to continue: ").strip()
    if answer != "CLEAR":
        raise SystemExit("[host] canceled")


def clear_filesystem(port):
    subprocess.run(
        [
            sys.executable,
            "-m",
            "mpremote",
            "connect",
            port,
            "fs",
            "rm",
            "-r",
            ":",
        ],
        cwd=PROJECT_DIR,
        check=True,
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port")
    parser.add_argument("--yes", action="store_true")
    args = parser.parse_args()

    port = args.port or choose_port()
    confirm_clear(port, args.yes)
    clear_filesystem(port)


if __name__ == "__main__":
    main()
