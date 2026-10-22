"""Single-process runner configuration; shared/public access is configured later."""
from pathlib import Path

chdir = str(Path(__file__).resolve().parents[3])
bind = "127.0.0.1:5005"
workers = 1
worker_class = "gthread"
threads = 16
timeout = 120
graceful_timeout = 30
keepalive = 5
preload_app = False
reload = False
max_requests = 0
accesslog = "-"
errorlog = "-"
capture_output = True
umask = 0o077
# No forwarding proxy is trusted until the HTTPS deployment is configured.
forwarded_allow_ips = ""
