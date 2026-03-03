import bleach


def sanitize_text(value: str, max_len: int | None = None) -> str:
    cleaned = bleach.clean(value or "", tags=[], attributes={}, strip=True)
    cleaned = cleaned.strip()
    if max_len is not None:
        return cleaned[:max_len]
    return cleaned
