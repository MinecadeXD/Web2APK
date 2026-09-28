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
VALUES_DIR = RES_DIR / "values"
FALLBACK_VECTOR = RES_DIR / "drawable" / "app_icon.xml"

APP_NAME_RE = re.compile(r"^.{1,60}$", re.DOTALL)
VERSION_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
PACKAGE_SUFFIX_RE = re.compile(r"^[a-z0-9]+(?:\.[a-z0-9]+)*$")
URL_RE = re.compile(r"^https://[^\s]+$", re.IGNORECASE)


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
        if source.suffix.lower() != ".png":
            fail("icon must point to a PNG file.")

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
    FALLBACK_VECTOR.unlink(missing_ok=True)
    image.save(DRAWABLE_DIR / "app_icon.png", format="PNG", optimize=True)


def write_resources(app_name: str, website_url: str, rgb: tuple[int, int, int]) -> None:
    VALUES_DIR.mkdir(parents=True, exist_ok=True)

    hex_color = "#{:02X}{:02X}{:02X}".format(*rgb)
    (VALUES_DIR / "colors.xml").write_text(
        f'''<?xml version="1.0" encoding="utf-8"?>
<resources>
    <color name="splash_background">{hex_color}</color>
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
    icon_path = required_string(data, "icon")

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
    write_resources(app_name, website_url, choose_background(image))

    safe_name = re.sub(r"[^A-Za-z0-9._-]+", "_", app_name).strip("._-") or "Website"

    write_github_env(
        {
            "WEB2APK_APP_NAME": app_name,
            "WEB2APK_WEBSITE_URL": website_url,
            "WEB2APK_VERSION": version,
            "WEB2APK_VERSION_CODE": str(version_code(version)),
            "WEB2APK_PACKAGE_SUFFIX": package_suffix,
            "WEB2APK_SAFE_NAME": safe_name,
        }
    )

    print("Configuration validated successfully.")
    print(f"App name:       {app_name}")
    print(f"Website URL:    {website_url}")
    print(f"Version:        {version}")
    print(f"Version code:   {version_code(version)}")
    print(f"Package name:   com.minecade.{package_suffix}")
    print(f"Icon source:    {icon_path}")


if __name__ == "__main__":
    main()
