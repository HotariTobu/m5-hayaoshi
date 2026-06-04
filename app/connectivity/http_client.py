import socket


def parse_http_url(url):
    prefix = "http://"
    if not url.startswith(prefix):
        raise ValueError("only http:// URLs are supported")

    rest = url[len(prefix):]
    slash = rest.find("/")
    if slash < 0:
        host_port = rest
        path = "/"
    else:
        host_port = rest[:slash]
        path = rest[slash:]

    colon = host_port.rfind(":")
    if colon >= 0:
        host = host_port[:colon]
        port = int(host_port[colon + 1:])
    else:
        host = host_port
        port = 80

    if not host:
        raise ValueError("HTTP host is missing")

    return host, port, path


def socket_write(sock, data):
    while data:
        sent = sock.send(data)
        if not sent:
            raise OSError("socket send failed")
        data = data[sent:]


def read_status_line(sock):
    line = b""
    while len(line) < 160:
        chunk = sock.recv(1)
        if not chunk:
            break
        line += chunk
        if chunk == b"\n":
            break
    return line


def post_status(url, timeout_sec):
    host, port, path = parse_http_url(url)
    addr = socket.getaddrinfo(host, port)[0][-1]
    sock = socket.socket()

    try:
        if hasattr(sock, "settimeout"):
            sock.settimeout(timeout_sec)
        sock.connect(addr)

        host_header = host if port == 80 else "{}:{}".format(host, port)
        request = (
            b"POST " + path.encode() + b" HTTP/1.1\r\n" +
            b"Host: " + host_header.encode() + b"\r\n" +
            b"Content-Length: 0\r\n" +
            b"Connection: close\r\n\r\n"
        )
        socket_write(sock, request)
        parts = read_status_line(sock).split()
        if len(parts) < 2:
            raise OSError("bad HTTP response")
        return int(parts[1])
    finally:
        sock.close()
