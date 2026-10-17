def like_pattern(v: str) -> str:
    """Contains-match pattern with LIKE wildcards in the user's text made literal."""
    esc = "\\"
    escaped = v.strip().replace(esc, esc * 2).replace("%", esc + "%").replace("_", esc + "_")
    return f"%{escaped}%"
