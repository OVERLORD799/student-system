import traceback
from datetime import datetime
from pathlib import Path
from typing import Optional

from django.conf import settings


def append_error_log(message: str, exc: Optional[BaseException] = None) -> None:
    path: Path = getattr(settings, "APP_LOG_FILE", Path("log.txt"))
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"{datetime.now().isoformat()}  {message}"]
    if exc is not None:
        lines.append(f"类型: {type(exc).__name__}")
        lines.append(traceback.format_exc())
    lines.append("")
    with path.open("a", encoding="utf-8") as f:
        f.write("\n".join(lines))
