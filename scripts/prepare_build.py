from __future__ import annotations

import os
import re
from pathlib import Path

import yaml
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "app.yml"
RES_DIR = ROOT / "app" / "src" / "main" / "res"
DRAWABLE_DIR = RES_DIR / "drawable-nodpi"
MIPMAP_DIR = RES_DIR / "mipmap-anydpi-v26"
VALUES_DIR = RES_DIR / "values"
FALLBACK_VECTOR = RES_DIR / "drawable" / "app_icon.xml"

APP_NAME_RE = re.compile(r"^.{1,60}$", re.DOTALL)
VERSION_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
PACKAGE_SUFFIX_RE = re.compile(r"^[a-z0-9]+(?:\.[a-z0-9]+)*$")
URL_RE = re.compile(r"^https://[^\s]+$", re.IGNORECASE)
HEX_COLOR_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")


def fail(message: str) -> None:
    raise SystemExit(f"Web2APK configuration error: {message}")


def required_string(data: dict, key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        fail(f"'{key}' must be a non-empty string.")
    return value.strip()


def version_code(version: str) -> int:
    major, minor, patch = (int(part) for part in version.split("."))
    code = major * 1_000_000 + minor * 1_000 + patch
    if code > 2_100_000_000:
        fail("version produces an Android versionCode above the supported range.")
    return code


def parse_bool(data: dict, key: str, default: bool) -> bool:
    value = data.get(key, default)
    if not isinstance(value, bool):
        fail(f"'{key}' must be true or false.")
    return value


def parse_color(data: dict, key: str, default: str) -> str:
    value = data.get(key, default)
    if not isinstance(value, str) or not value.strip():
        fail(f"'{key}' must be a color name (white/black) or a 6-digit hex color.")
    value = value.strip().lower()
    if value in {"white", "black"}:
        return "#FFFFFF" if value == "white" else "#000000"
    if HEX_COLOR_RE.fullmatch(value):
        return value.upper()
    fail(f"'{key}' must be 'white', 'black', or a 6-digit hex color such as #121212.")


def xml_escape(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def choose_background(image: Image.Image) -> tuple[int, int, int]:
    rgba = image.convert("RGBA")
    samples = []
    size = max(1, min(rgba.width, rgba.height) // 20)

    for box in [
        (0, 0, size, size),
        (rgba.width - size, 0, rgba.width, size),
        (0, rgba.height - size, size, rgba.height),
        (rgba.width - size, rgba.height - size, rgba.width, rgba.height),
    ]:
        for r, g, b, a in rgba.crop(box).getdata():
            if a >= 230:
                samples.append((r, g, b))

    if not samples:
        return (255, 255, 255)

    r = sum(p[0] for p in samples) / len(samples)
    g = sum(p[1] for p in samples) / len(samples)
    b = sum(p[2] for p in samples) / len(samples)
    luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b

    return (255, 255, 255) if luminance >= 128 else (0, 0, 0)


def generate_fallback_icon(app_name: str) -> Image.Image:
    image = Image.new("RGBA", (1024, 1024), (255, 255, 255, 255))
    draw = ImageDraw.Draw(image)

    ascii_letters = [c for c in app_name if ("A" <= c <= "Z") or ("a" <= c <= "z")]
    letter = (ascii_letters[0] if ascii_letters else app_name[0]).upper()

    try:
        font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            560,
        )
    except OSError:
        font = ImageFont.load_default()

    box = draw.textbbox((0, 0), letter, font=font)
    x = (1024 - (box[2] - box[0])) / 2 - box[0]
    y = (1024 - (box[3] - box[1])) / 2 - box[1]
    draw.text((x, y), letter, fill=(0, 0, 0, 255), font=font)

    return image


def load_icon(icon_path: str, app_name: str) -> Image.Image:
    source = ROOT / icon_path

    if source.is_file():
        if source.suffix.lower() not in {".png", ".jpg", ".jpeg"}:
            fail("icon must point to a PNG, JPG, or JPEG file.")

        try:
            image = Image.open(source).convert("RGBA")
        except Exception as exc:
            fail(f"could not read icon '{icon_path}': {exc}")

        if image.width < 192 or image.height < 192:
            fail("icon must be at least 192x192 pixels.")

        return ImageOps.contain(
            image,
            (1024, 1024),
            method=Image.Resampling.LANCZOS,
        )

    print(f"Icon '{icon_path}' was not found; generating the automatic letter icon.")
    return generate_fallback_icon(app_name)


def write_icon(image: Image.Image) -> None:
    DRAWABLE_DIR.mkdir(parents=True, exist_ok=True)
    MIPMAP_DIR.mkdir(parents=True, exist_ok=True)
    FALLBACK_VECTOR.unlink(missing_ok=True)

    # Keep the full-size launcher icon, but create a padded copy for the
    # Android 12+ splash screen. The splash icon is masked, so padding keeps
    # artwork near the edges from being clipped.
    image.save(DRAWABLE_DIR / "app_icon.png", format="PNG", optimize=True)

    # Generate a padded adaptive-icon foreground so Android launchers can apply
    # their shape mask without clipping the supplied artwork.
    adaptive_foreground = Image.new("RGBA", (1024, 1024), (0, 0, 0, 0))
    adaptive_image = ImageOps.contain(image, (720, 720), method=Image.Resampling.LANCZOS)
    x = (1024 - adaptive_image.width) // 2
    y = (1024 - adaptive_image.height) // 2
    adaptive_foreground.alpha_composite(adaptive_image, (x, y))
    adaptive_foreground.save(DRAWABLE_DIR / "app_icon_foreground.png", format="PNG", optimize=True)

    (MIPMAP_DIR / "app_icon.xml").write_text(
        '<?xml version="1.0" encoding="utf-8"?>\n<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">\n    <background android:drawable="@color/app_icon_background" />\n    <foreground android:drawable="@drawable/app_icon_foreground" />\n</adaptive-icon>\n',
        encoding="utf-8",
    )

    splash = Image.new("RGBA", (1024, 1024), (0, 0, 0, 0))
    splash_size = 640
    splash_image = ImageOps.contain(
        image,
        (splash_size, splash_size),
        method=Image.Resampling.LANCZOS,
    )
    x = (1024 - splash_image.width) // 2
    y = (1024 - splash_image.height) // 2
    splash.alpha_composite(splash_image, (x, y))
    splash.save(DRAWABLE_DIR / "splash_icon.png", format="PNG", optimize=True)


def write_resources(app_name: str, website_url: str, splash_background: str, toolbar_color: str, show_title: bool, url_bar_hiding: bool) -> None:
    VALUES_DIR.mkdir(parents=True, exist_ok=True)

    hex_color = splash_background
    (VALUES_DIR / "colors.xml").write_text(
        f'''<?xml version="1.0" encoding="utf-8"?>
<resources>
    <color name="splash_background">{hex_color}</color>
    <color name="app_icon_background">{hex_color}</color>\n    <color name="toolbar_color">{toolbar_color}</color>
</resources>
''',
        encoding="utf-8",
    )

    (VALUES_DIR / "generated.xml").write_text(
        f'''<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="app_name">{xml_escape(app_name)}</string>
    <string name="website_url">{xml_escape(website_url)}</string>
</resources>
''',
        encoding="utf-8",
    )


def write_github_env(values: dict[str, str]) -> None:
    env_path = os.environ.get("GITHUB_ENV")
    if not env_path:
        fail("GITHUB_ENV is not available; this script must run in GitHub Actions.")

    with open(env_path, "a", encoding="utf-8") as env:
        for key, value in values.items():
            env.write(f"{key}<<WEB2APK_EOF\n{value}\nWEB2APK_EOF\n")


def main() -> None:
    if not CONFIG_PATH.is_file():
        fail("config/app.yml is missing.")

    try:
        data = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        fail(f"invalid YAML: {exc}")

    if not isinstance(data, dict):
        fail("config/app.yml must contain a YAML mapping.")

    app_name = required_string(data, "app_name")
    website_url = required_string(data, "website_url")
    version = required_string(data, "version")
    package_suffix = required_string(data, "package_suffix")
    icon_path = required_string(data, "icon")\n    splash_background = parse_color(data, "splash_background", "white")\n    toolbar_color = parse_color(data, "toolbar_color", "#121212")\n    show_title = parse_bool(data, "show_title", True)\n    url_bar_hiding = parse_bool(data, "url_bar_hiding", True)

    if not APP_NAME_RE.fullmatch(app_name):
        fail("app_name must contain 1-60 characters.")

    if not URL_RE.fullmatch(website_url):
        fail("website_url must be a complete HTTPS URL.")

    if not VERSION_RE.fullmatch(version):
        fail("version must use MAJOR.MINOR.PATCH format, for example 1.0.0.")

    if not PACKAGE_SUFFIX_RE.fullmatch(package_suffix):
        fail(
            "package_suffix may contain only lowercase letters, numbers, and periods; "
            "each segment must start and end with a letter or number."
        )

    if package_suffix.startswith("debug") or package_suffix.endswith(".debug"):
        fail("package_suffix cannot produce a reserved debug package name.")

    if len(package_suffix) > 80:
        fail("package_suffix must be 80 characters or fewer.")

    image = load_icon(icon_path, app_name)
    write_icon(image)
    write_resources(app_name, website_url, splash_background, toolbar_color, show_title, url_bar_hiding)

    safe_name = re.sub(r"\s+", " ", app_name).strip()
    safe_name = re.sub(r"[^A-Za-z0-9._ -]+", "_", safe_name).strip(" ._-") or "Website"

    write_github_env(
        {
            "WEB2APK_APP_NAME": app_name,
            "WEB2APK_WEBSITE_URL": website_url,
            "WEB2APK_VERSION": version,
            "WEB2APK_VERSION_CODE": str(version_code(version)),
            "WEB2APK_PACKAGE_SUFFIX": package_suffix,
            "WEB2APK_SAFE_NAME": safe_name,\n            "WEB2APK_SPLASH_BACKGROUND": splash_background,\n            "WEB2APK_TOOLBAR_COLOR": toolbar_color,\n            "WEB2APK_SHOW_TITLE": str(show_title).lower(),\n            "WEB2APK_URL_BAR_HIDING": str(url_bar_hiding).lower(),
        }
    )

    print("Configuration validated successfully.")
    print(f"App name:       {app_name}")
    print(f"Website URL:    {website_url}")
    print(f"Version:        {version}")
    print(f"Version code:   {version_code(version)}")
    print(f"Package name:   com.minecade.{package_suffix}")
    print(f"Icon source:    {icon_path}")\n    print(f"Splash color:   {splash_background}")\n    print(f"Toolbar color:  {toolbar_color}")\n    print(f"Show title:     {show_title}")\n    print(f"URL bar hiding: {url_bar_hiding}")


if __name__ == "__main__":
    main()
