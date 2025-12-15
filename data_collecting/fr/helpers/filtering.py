import unicodedata
import re

FRENCH_LETTERS = "abcdefghijklmnopqrstuvwxyzàâæçéèêëîïôœùûüÿ"

def is_mostly_french_letters_and_punct(s, min_ratio=0.7):
    """
    Keep sentences where at least `min_ratio` of chars are
    French/Latin letters, spaces or common punctuation.
    """
    allowed = set(FRENCH_LETTERS + " " + ".,;:!?\"'()[]{}-")
    s_lower = s.lower()
    if not s_lower:
        return False

    good = sum(ch in allowed for ch in s_lower)
    ratio = good / len(s_lower)
    return ratio >= min_ratio


def looks_like_clean_french(sent: str) -> bool:
    s = sent.strip()

    # 1) Filter out obvious noise: urls, mentions, hashtags
    if any(token in s for token in ("http://", "https://", "www.", "@", "#")):
        return False

    # 2) Filter out too many digits
    digits = sum(c.isdigit() for c in s)
    if digits > len(s) * 0.2:  # > 20% digits -> likely tables, lists, etc.
        return False

    # 3) Check mostly French/Latin letters & punctuation
    if not is_mostly_french_letters_and_punct(s, min_ratio=0.7):
        return False

    return True


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
