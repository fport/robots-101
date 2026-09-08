"""Yerel önbellekler ve açık hata kontrolü; robot bağlantısı başlatmaz."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def prepare_paths():
    for key, relative in {
        "STRANDS_BASE_DIR": ".cache/strands",
        "STRANDS_ASSETS_DIR": ".cache/strands-assets",
        "ROBOT_DESCRIPTIONS_CACHE": ".cache/robot-descriptions",
        "HF_HOME": ".cache/huggingface",
        "STRANDS_ROBOTS_RENDER_ROOT": "outputs/renders",
    }.items():
        os.environ.setdefault(key, str(ROOT / relative))
    (ROOT / "outputs").mkdir(exist_ok=True)


def checked(result, operation):
    if not isinstance(result, dict) or result.get("status") != "success":
        raise RuntimeError(f"{operation} başarısız: {result}")
    return result


def payload(result):
    return next((item["json"] for item in result.get("content", []) if "json" in item), {})


def save_render(result, path):
    checked(result, "render")
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    for item in result.get("content", []):
        if "image" in item:
            raw = item["image"]["source"]["bytes"]
            if isinstance(raw, str):
                import base64
                raw = base64.b64decode(raw)
            path.write_bytes(raw)
            return path
    raise RuntimeError("Render başarılı bildirdi ancak görüntü döndürmedi.")
