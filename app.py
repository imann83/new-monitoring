
from flask import Flask, jsonify, render_template_string
import asyncio
from monitor_async import AsyncSkinBaronMonitor
import threading

SKINBARON_URL = "https://skinbaron.de/en/csgo?plb=0.04&pub=71.5&sort=BP"
monitor = AsyncSkinBaronMonitor(SKINBARON_URL)

app = Flask(__name__)

HTML_TEMPLATE = '''
<html><head><title>Status</title></head><body>
<h2>SkinBaron Async Monitor</h2>
<p>Status: {{ 'Running' if status.is_running else 'Stopped' }}</p>
<p>Start Time: {{ status.start_time }}</p>
<p>Last Check: {{ status.last_check }}</p>
<p>Total Checks: {{ status.total_checks }}</p>
<p>Last Error: {{ status.last_error or 'None' }}</p>
</body></html>
'''

@app.route("/")
def dashboard():
    return render_template_string(HTML_TEMPLATE, status=monitor.status)

@app.route("/api/status")
def api_status():
    return jsonify({
        "status": "running" if monitor.status["is_running"] else "stopped",
        "start_time": str(monitor.status["start_time"]),
        "last_check": str(monitor.status["last_check"]),
        "total_checks": monitor.status["total_checks"],
        "last_error": monitor.status["last_error"]
    })

def start_async_monitor():
    asyncio.run(monitor.run())

if __name__ == "__main__":
    threading.Thread(target=start_async_monitor, daemon=True).start()
    app.run(host="0.0.0.0", port=5000)
