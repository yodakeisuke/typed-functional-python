def existence_check_japanese_address(pref: str, detail: str) -> bool:
    return pref not in ("無い県", "ない県")
