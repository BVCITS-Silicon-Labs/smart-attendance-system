import requests
from ..config import settings

# Last requested LED state. This is only the server's last command,
# not a hardware sensor reading.
_last_color = "blue"


def device_url(path: str) -> str:
    return f"http://{settings.device_ip}:{settings.device_port}{path}"


def health() -> bool:
    try:
        r = requests.get(
            device_url("/health"),
            params={"key": settings.device_api_key},
            timeout=1.5,
        )
        return r.ok
    except requests.RequestException:
        return False


def set_led(color: str):
    global _last_color

    color = color.strip().lower()
    if color not in {"red", "green", "blue"}:
        return False, "Invalid LED color"

    try:
        r = requests.get(
            device_url("/led"),
            params={
                "color": color,
                "key": settings.device_api_key,
            },
            timeout=2,
        )

        if r.ok:
            _last_color = color

        return r.ok, r.text[:500]

    except requests.RequestException as exc:
        return False, str(exc)


def get_last_color() -> str:
    return _last_color
