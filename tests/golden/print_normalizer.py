import re

ESC = r"\x1b"
CTRL = r"[\x00-\x1F\x7F]"
CSI = rf"{ESC}\[[0-?]*[ -/]*[@-~]"


def normalize_legacy_print(s: str) -> str:
    s = re.sub(CSI, "", s)
    s = re.sub(rf"{ESC}[^A-Za-z]", "", s)
    s = re.sub(CTRL, lambda m: "\n" if m.group(0) in ("\r", "\n") else "", s)
    s = re.sub(r"[ \t]{2,}", " ", s)
    s = "\n".join(line.rstrip() for line in s.splitlines())
    return "\n".join([ln for ln in s.splitlines() if ln.strip()])[:10000]
