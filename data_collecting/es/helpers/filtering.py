import unicodedata
import re

INVISIBLE_CATEGORIES = {"Cf", "Cc"}  # format & control chars

def remove_invisible_chars(s: str) -> str:
    # 1) map weird spaces to normal space
    s = s.replace('\u00A0', ' ')   # no-break space
    # 2) drop zero-width / directional marks etc.
    s = ''.join(
        ch for ch in s
        if unicodedata.category(ch) not in INVISIBLE_CATEGORIES
    )
    # 3) normalize whitespace
    s = re.sub(r'\s+', ' ', s).strip()
    return s


# ---- Spanish-specific helpers ----

SPANISH_LETTERS = "abcdefghijklmnopqrstuvwxyzáéíóúüñ"

def is_mostly_spanish_letters_and_punct(s: str, min_ratio: float = 0.7) -> bool:
    """
    Keep sentences where at least `min_ratio` of chars are
    Spanish/Latin letters, spaces or common punctuation.
    """
    allowed = set(SPANISH_LETTERS + " " + ".,;:!?\"'()[]{}-")
    s_lower = s.lower()
    if not s_lower:
        return False

    good = sum(ch in allowed for ch in s_lower)
    ratio = good / len(s_lower)
    return ratio >= min_ratio


def looks_like_clean_spanish(sent: str) -> bool:
    s = sent.strip()
    if not s:
        return False

    # 1) Filter out URLs / mentions / hashtags
    if any(tok in s for tok in ("http://", "https://", "www.", "@", "#")):
        return False

    # 2) Filter out too many digits (tables, lists of years, etc.)
    digits = sum(c.isdigit() for c in s)
    if digits > len(s) * 0.2:  # >20% of chars are digits
        return False

    # 3) Must be mostly Spanish letters & punctuation
    if not is_mostly_spanish_letters_and_punct(s, min_ratio=0.7):
        return False

    return True
