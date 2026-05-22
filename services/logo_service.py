import os
import shutil
import uuid

from PIL import Image

from config import LOGO_ALLOWED, LOGO_DIR, LOGO_DISPLAY_SIZE, LOGO_THUMB_SIZE


def _session_dir(session_id: str) -> str:
    path = os.path.join(LOGO_DIR, session_id)
    os.makedirs(path, exist_ok=True)
    return path


def allowed_file(filename: str) -> bool:
    if not filename or "." not in filename:
        return False
    return filename.rsplit(".", 1)[1].lower() in LOGO_ALLOWED


def save_upload(session_id: str, file_storage) -> dict:
    ext = file_storage.filename.rsplit(".", 1)[1].lower()
    dest_dir = _session_dir(session_id)
    for f in os.listdir(dest_dir):
        if f.startswith("original."):
            os.remove(os.path.join(dest_dir, f))
    original = os.path.join(dest_dir, f"original.{ext}")
    file_storage.save(original)
    return {"path": original, "ext": ext, "is_svg": ext == "svg"}


def apply_crop(
    session_id: str,
    crop: dict | None,
    fit: str = "cover",
) -> dict:
    dest_dir = _session_dir(session_id)
    original = _find_original(dest_dir)
    if not original:
        raise FileNotFoundError("Nessun logo caricato")
    ext = original.rsplit(".", 1)[-1].lower()
    display_path = os.path.join(dest_dir, "display.png")
    thumb_path = os.path.join(dest_dir, "thumb.png")

    if ext == "svg":
        shutil.copy(original, os.path.join(dest_dir, "display.svg"))
        shutil.copy(original, os.path.join(dest_dir, "thumb.svg"))
        return {
            "display": "display.svg",
            "thumb": "thumb.svg",
            "format": "svg",
        }

    img = Image.open(original)
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGBA")
    else:
        img = img.convert("RGB")

    if crop:
        x = int(crop.get("x", 0))
        y = int(crop.get("y", 0))
        w = int(crop.get("width", img.width))
        h = int(crop.get("height", img.height))
        img = img.crop((x, y, x + w, y + h))

    img = _fit_image(img, LOGO_DISPLAY_SIZE, fit)
    _save_png(img, display_path)

    thumb = _fit_image(img.copy(), LOGO_THUMB_SIZE, "cover")
    _save_png(thumb, thumb_path)

    return {"display": "display.png", "thumb": "thumb.png", "format": "png"}


def _find_original(dest_dir: str) -> str | None:
    if not os.path.isdir(dest_dir):
        return None
    for name in os.listdir(dest_dir):
        if name.startswith("original."):
            return os.path.join(dest_dir, name)
    return None


def _fit_image(img: Image.Image, size: tuple, fit: str) -> Image.Image:
    tw, th = size
    if fit == "contain":
        img.thumbnail((tw, th), Image.Resampling.LANCZOS)
        canvas = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
        ox = (tw - img.width) // 2
        oy = (th - img.height) // 2
        canvas.paste(img, (ox, oy), img if img.mode == "RGBA" else None)
        return canvas
    return ImageOps_fit_cover(img, tw, th)


def ImageOps_fit_cover(img: Image.Image, tw: int, th: int) -> Image.Image:
    ratio = max(tw / img.width, th / img.height)
    nw, nh = int(img.width * ratio), int(img.height * ratio)
    img = img.resize((nw, nh), Image.Resampling.LANCZOS)
    left = (nw - tw) // 2
    top = (nh - th) // 2
    return img.crop((left, top, left + tw, top + th))


def _save_png(img: Image.Image, path: str) -> None:
    if img.mode == "RGBA":
        img.save(path, "PNG", optimize=True)
    else:
        img.save(path, "PNG", optimize=True)


def remove_logo(session_id: str) -> None:
    dest_dir = os.path.join(LOGO_DIR, session_id)
    if os.path.isdir(dest_dir):
        shutil.rmtree(dest_dir)


def logo_urls(session_id: str, meta_logo: dict | None) -> dict:
    if not meta_logo:
        return {"display": None, "thumb": None}
    base = f"/loghi/{session_id}"
    return {
        "display": f"{base}/{meta_logo.get('display')}" if meta_logo.get("display") else None,
        "thumb": f"{base}/{meta_logo.get('thumb')}" if meta_logo.get("thumb") else None,
    }


def update_session_logo(session: dict, logo_info: dict) -> None:
    session.setdefault("meta", {})["logo"] = logo_info


def has_pending_original(session_id: str) -> bool:
    dest_dir = os.path.join(LOGO_DIR, session_id)
    if not os.path.isdir(dest_dir):
        return False
    return _find_original(dest_dir) is not None
