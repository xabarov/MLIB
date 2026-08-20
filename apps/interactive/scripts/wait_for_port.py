from __future__ import annotations

import argparse
import socket
import time


def wait_for_port(host: str, port: int, timeout: float) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection((host, port), timeout=1):
                return
        except OSError:
            time.sleep(0.25)
    raise SystemExit(f"Timed out waiting for {host}:{port}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--timeout", type=float, default=45)
    args = parser.parse_args()
    wait_for_port(args.host, args.port, args.timeout)


if __name__ == "__main__":
    main()
