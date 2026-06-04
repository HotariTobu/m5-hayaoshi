import argparse
from datetime import datetime

from flask import Flask, request


HOST = "0.0.0.0"

app = Flask(__name__)


@app.post("/api/act/<device_id>")
def act(device_id):
    status = app.config["status_code"]
    print(
        f"{datetime.now().isoformat(timespec='seconds')} "
        f"POST {request.path} device_id={device_id} status={status}",
        flush=True,
    )
    return "", status


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("port", type=int)
    parser.add_argument("status_code", nargs="?", type=int, default=200)
    return parser.parse_args()


def main():
    args = parse_args()
    if args.port < 1 or args.port > 65535:
        raise SystemExit("port must be between 1 and 65535")
    if args.status_code < 100 or args.status_code > 599:
        raise SystemExit("status_code must be between 100 and 599")

    app.config["status_code"] = args.status_code
    print(f"status={args.status_code}", flush=True)
    app.run(host=HOST, port=args.port)


if __name__ == "__main__":
    main()
