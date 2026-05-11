#!/usr/bin/env python3
"""CORS proxy for Volce Ark API."""
import http.server
import http.client
import socketserver

PORT = 8888
TARGET_HOST = "ark.cn-beijing.volces.com"
TARGET_PORT = 443

class Proxy(http.server.BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.0'
    def log_message(self, fmt, *args): print(f"[proxy] {fmt%args}")
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()
    def do_POST(self):
        body_len = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(body_len)
        conn = http.client.HTTPSConnection(TARGET_HOST, TARGET_PORT)
        fwd = {}
        for k, v in self.headers.items():
            if k.lower() not in ("host", "content-length", "connection"):
                fwd[k] = v
        conn.request("POST", "/api/coding/v1/chat/completions", body, fwd)
        resp = conn.getresponse()
        self.send_response(resp.status)
        self.send_header("Access-Control-Allow-Origin", "*")
        for k, v in resp.getheaders():
            if k.lower() not in ("transfer-encoding", "host", "connection"):
                self.send_header(k, v)
        self.end_headers()
        self.wfile.write(resp.read())
        conn.close()

socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(("", PORT), Proxy) as h:
    print(f"CORS proxy running on :{PORT}")
    h.serve_forever()
