import re
import unicodedata


def format_ball_filename(name: str, suffix: str):
    return f"{name.lower().replace(' ', '-')}{suffix}"


def sanitize_ball_emoji_name(name: str):
    name = unicodedata.normalize("NFKD", name)
    name = name.encode("ascii", "ignore").decode("ascii")
    name = re.sub(r"[^A-Za-z0-9_]", "_", name)
    name = re.sub(r"_+", "_", name).strip("_")
    return name
