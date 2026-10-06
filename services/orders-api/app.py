import os, time, uuid, json, logging
from flask import Flask, request, g, jsonify
from prometheus_client import Counter, Histogram, generate_latest

app = Flask(__name__)
REQS = Counter("nsp_requests_total", "HTTP requests", ["route", "method", "code"])
LAT = Histogram("nsp_request_seconds", "Latency", ["route"], buckets=(0.05, 0.1, 0.2, 0.3, 0.5, 1, 2))
log = logging.getLogger("nsp")

def secret(name):
    try:
        with open(f"/mnt/secrets/{name}") as f:
            return f.read().strip()
    except FileNotFoundError:
        return "placeholder"

@app.before_request
def _start():
    g.t0 = time.perf_counter()
    g.rid = request.headers.get("X-Request-ID", str(uuid.uuid4()))

@app.after_request
def _record(resp):
    route = request.url_rule.rule if request.url_rule else "unmatched"
    dur = time.perf_counter() - getattr(g, 't0', time.perf_counter())
    REQS.labels(route, request.method, str(resp.status_code)).inc()
    LAT.labels(route).observe(dur)
    resp.headers["X-Request-ID"] = getattr(g, 'rid', 'unknown')
    return resp

@app.route("/health")
def health():
    return jsonify({"status": "ok", "db_host": secret("db-host")})

@app.route("/metrics")
def metrics():
    return generate_latest()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
