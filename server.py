import ujson
import argparse
import ssl
import sys
import time
from api_handler import compute_recipes
from http.server import BaseHTTPRequestHandler,HTTPServer
from socketserver import ThreadingMixIn
from urllib.parse import urlparse, parse_qsl


class Server(BaseHTTPRequestHandler):

    my_time = 1

    def do_POST(self):  # noqa N802
        new_time = time.time()
        if new_time - Server.my_time < 60:
            message = "Forbidden"
            self._set_headers(403, length=len(message))
            self.wfile.write(message.encode("utf-8"))
            return
        Server.my_time = new_time
        content_len = int(self.headers.get("Content-Length"))
        post_body = self.rfile.read(content_len)
        js = compute_recipes(post_body)
        self._set_headers(200, content="application/json")
        self.wfile.write(js.encode("utf-8"))

    def _set_headers(self, response, content="text/xml", length=None):
        self.send_response(response)
        self.send_header("Content-Type", content)
        if length:
            self.send_header("Content-Length", length)
        self.end_headers()


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""


def run_server(port, certificate=None, key=None):
    server_address = ("0.0.0.0", port)
    httpd = ThreadedHTTPServer(server_address, Server)
    if certificate:
        if key:
            httpd.socket = ssl.wrap_socket(httpd.socket, certfile=certificate, keyfile=key, server_side=True)
        else:
            httpd.socket = ssl.wrap_socket(httpd.socket, certfile=certificate, server_side=True)
    print(
        "Starting {PROTOCOL} server on port {PORT}, use <Ctrl-C> to stop".format(
            PROTOCOL="HTTPS" if certificate else "HTTP", PORT=port
        )
    )
    httpd.serve_forever()


def get_arguments():
    parser = argparse.ArgumentParser(description="Simple Server")
    parser.add_argument(
        "--certificate", help="The certificate to use for the external authenticator to run in HTTPS. Has to be .pem"
    )
    parser.add_argument("--key", help="The .key of the certificate, if not included in it")
    return parser.parse_args()

def main():
    try:
        args = get_arguments()
        # cleaning up the directory containing old files
        run_server(port=8444, certificate=args.certificate, key=args.key)
    except KeyboardInterrupt:
        print("Closing the server")
    except Exception as e:
        print("Unexpected error of type {0}: {1}".format(type(e).__name__, e))
        sys.exit(1)


if __name__ == "__main__":
    main()