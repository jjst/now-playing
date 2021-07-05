import redis
import http.server
import socketserver


PORT = 8001


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(s):
        """Respond to a GET request."""
        redis_client = redis.Redis(
            "0.0.0.0",
            6379,
            0,
        )
        redis_client.ping()
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()
        s.wfile.write(b"OK")


with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print("serving at port", PORT)
    httpd.serve_forever()
