import argparse
import html.parser
import pathlib
import re
import subprocess
import sys
import urllib.parse
import urllib.request

from select_port import choose_port


PROJECT_DIR = pathlib.Path(__file__).resolve().parent.parent
FIRMWARE_DIR = PROJECT_DIR / ".firmware"
FIRMWARE_PAGE_URL = "https://www.micropython.org/download/ESP32_GENERIC/"
FIRMWARE_FILE_RE = re.compile(r"ESP32_GENERIC-\d{8}-v[0-9][^/]*\.bin$")


class FirmwareLinkParser(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag != "a":
            return

        attrs_by_name = dict(attrs)
        href = attrs_by_name.get("href")
        if href:
            self.links.append(href)


def parse_offset(value):
    try:
        return int(value, 0)
    except ValueError:
        raise argparse.ArgumentTypeError("offset must be an integer like 0x1000")


def validate_firmware(path):
    firmware = pathlib.Path(path).expanduser().resolve()
    if not firmware.exists():
        raise SystemExit("[host] firmware not found: {}".format(firmware))
    if firmware.suffix.lower() != ".bin":
        raise SystemExit("[host] firmware must be a .bin file: {}".format(firmware))
    return firmware


def read_url(url):
    with urllib.request.urlopen(url) as response:
        return response.read()


def latest_stable_firmware_url():
    print("[host] resolving latest ESP32_GENERIC firmware", flush=True)
    print("[host] {}".format(FIRMWARE_PAGE_URL), flush=True)
    parser = FirmwareLinkParser()
    parser.feed(read_url(FIRMWARE_PAGE_URL).decode("utf-8", "replace"))

    for href in parser.links:
        url = urllib.parse.urljoin(FIRMWARE_PAGE_URL, href)
        filename = pathlib.PurePosixPath(urllib.parse.urlparse(url).path).name
        if FIRMWARE_FILE_RE.match(filename) and "preview" not in filename:
            print("[host] latest stable firmware: {}".format(filename), flush=True)
            return url

    raise SystemExit("[host] ESP32_GENERIC firmware link not found")


def firmware_path_for_url(url):
    filename = pathlib.PurePosixPath(urllib.parse.urlparse(url).path).name
    if not FIRMWARE_FILE_RE.match(filename):
        raise SystemExit("[host] unexpected firmware filename: {}".format(filename))
    return FIRMWARE_DIR / filename


def download_firmware(url, force):
    path = firmware_path_for_url(url)
    FIRMWARE_DIR.mkdir(exist_ok=True)
    if path.exists() and not force:
        print("[host] firmware exists: {}".format(path), flush=True)
        return path

    print("[host] downloading firmware:", flush=True)
    print("[host] {}".format(url), flush=True)
    data = read_url(url)

    tmp_path = path.with_suffix(".bin.tmp")
    tmp_path.write_bytes(data)
    tmp_path.rename(path)
    print("[host] saved firmware: {}".format(path), flush=True)
    return path


def newest_cached_firmware():
    candidates = sorted(FIRMWARE_DIR.glob("ESP32_GENERIC-*-v*.bin"), reverse=True)
    candidates = [path for path in candidates if "preview" not in path.name]
    return candidates[0] if candidates else None


def resolve_firmware(path_arg, use_cached, force_download):
    if path_arg:
        return validate_firmware(path_arg)
    if use_cached and not force_download:
        cached = newest_cached_firmware()
        if cached:
            print("[host] using cached firmware: {}".format(cached), flush=True)
            return validate_firmware(cached)
    return validate_firmware(download_firmware(latest_stable_firmware_url(), force_download))


def confirm_flash(port, firmware, skip_erase, yes):
    print("[host] port: {}".format(port), flush=True)
    print("[host] firmware: {}".format(firmware), flush=True)
    if skip_erase:
        print("[host] erase: skipped", flush=True)
        return

    print("[host] erase: entire flash will be erased", flush=True)
    if yes:
        return

    answer = input("[host] type ERASE to continue: ").strip()
    if answer != "ERASE":
        raise SystemExit("[host] canceled")


def run(command):
    print("[host] {}".format(" ".join(str(part) for part in command)), flush=True)
    subprocess.run(command, cwd=PROJECT_DIR, check=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--firmware", help="MicroPython ESP32 .bin file")
    parser.add_argument("--use-cached", action="store_true", help="skip latest check and use newest cached firmware")
    parser.add_argument("--force-download", action="store_true")
    parser.add_argument("--port")
    parser.add_argument("--baud", type=int, default=460800)
    parser.add_argument("--offset", type=parse_offset, default=0x1000)
    parser.add_argument("--chip", default="esp32")
    parser.add_argument("--skip-erase", action="store_true")
    parser.add_argument("--yes", action="store_true", help="skip ERASE confirmation")
    args = parser.parse_args()

    firmware = resolve_firmware(args.firmware, args.use_cached, args.force_download)
    port = args.port or choose_port()
    confirm_flash(port, firmware, args.skip_erase, args.yes)

    base = [sys.executable, "-m", "esptool", "--chip", args.chip, "--port", port]
    if not args.skip_erase:
        run(base + ["erase-flash"])

    run(
        base
        + [
            "--baud",
            str(args.baud),
            "write-flash",
            "--compress",
            hex(args.offset),
            str(firmware),
        ]
    )
    print("[host] MicroPython firmware flash complete", flush=True)


if __name__ == "__main__":
    main()
