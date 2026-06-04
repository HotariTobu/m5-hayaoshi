from serial.tools import list_ports


def describe_port(port):
    parts = [port.device]
    if port.description:
        parts.append(port.description)
    if port.manufacturer:
        parts.append(port.manufacturer)
    return " - ".join(parts)


def choose_port():
    candidates = list(list_ports.comports())
    if not candidates:
        raise SystemExit("[host] no serial port candidates found")

    print("[host] serial port candidates:")
    for index, port in enumerate(candidates, 1):
        print("[{}] {}".format(index, describe_port(port)))

    while True:
        try:
            answer = input("[host] select port number: ").strip()
        except EOFError:
            raise SystemExit("[host] port selection requires stdin")

        try:
            index = int(answer)
        except ValueError:
            print("[host] enter a number")
            continue

        if 1 <= index <= len(candidates):
            return candidates[index - 1].device

        print("[host] number out of range")
