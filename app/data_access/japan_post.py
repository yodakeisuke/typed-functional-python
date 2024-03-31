def existence_check_japanese_address(prefecture: str, detail: str) -> bool:
    return prefecture not in ("無い県", "ない県")
