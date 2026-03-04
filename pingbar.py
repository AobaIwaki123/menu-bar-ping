import re
import subprocess
import rumps

PING_HOST = "8.8.8.8"
PING_INTERVAL = 2.0  # seconds


def measure_ping(host: str) -> float | None:
    """Return round-trip time in ms, or None on failure."""
    try:
        result = subprocess.run(
            ["/sbin/ping", "-c", "1", "-W", "1000", host],
            capture_output=True,
            text=True,
            timeout=3,
        )
        match = re.search(r"time=(\d+(?:\.\d+)?)", result.stdout)
        return float(match.group(1)) if match else None
    except (subprocess.TimeoutExpired, OSError):
        return None


def format_title(ms: float | None) -> str:
    if ms is None:
        return "ping: --"
    return f"ping: {ms:.0f}ms"


class PingBarApp(rumps.App):
    def __init__(self):
        super().__init__(name="PingBar", title="ping: …", quit_button="Quit")
        self.menu = [
            rumps.MenuItem("Host: " + PING_HOST),
            None,  # separator
        ]

    @rumps.timer(PING_INTERVAL)
    def update(self, _):
        ms = measure_ping(PING_HOST)
        self.title = format_title(ms)


if __name__ == "__main__":
    PingBarApp().run()
