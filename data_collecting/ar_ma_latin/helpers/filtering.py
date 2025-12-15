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


# ---------- pure Latin Arabizi helpers ----------

def contains_arabic_script(s: str) -> bool:
    """True if any Arabic-script character appears."""
    for ch in s:
        if (
            '\u0600' <= ch <= '\u06FF' or
            '\u0750' <= ch <= '\u077F' or
            '\u08A0' <= ch <= '\u08FF' or
            '\uFB50' <= ch <= '\uFDFF' or
            '\uFE70' <= ch <= '\uFEFF'
        ):
            return True
    return False


def looks_like_ar_ma_latn_pure(sent: str,
                               min_words: int = 2,
                               max_digit_ratio: float = 0.6) -> bool:
    """
    Heuristic filter for *pure Latin* Moroccan Arabizi (ar_ma_latn).
    - Only [a-z] letters allowed, no accented letters, no Arabic script.
    - Reject URLs, hashtags, mentions.
    - Reject lines that are mostly digits or symbols.
    """
    s = sent.strip()
    if not s:
        return False

    # 0) Obvious junk: URLs / mentions / hashtags
    if any(tok in s for tok in ("http://", "https://", "www.", "@", "#")):
        return False

    # 1) No Arabic script at all
    if contains_arabic_script(s):
        return False

    # 2) Only ASCII latin letters allowed
    letters = 0
    digits = 0
    for ch in s:
        if ch.isalpha():
            # reject any non [a-z]
            if not ('a' <= ch.lower() <= 'z'):
                return False
            letters += 1
        elif ch.isdigit():
            digits += 1
        else:
            # punctuation / space / emoji etc. are allowed; we filter later by ratios
            continue

    # 3) Enough letters (avoid pure numbers / codes)
    if letters == 0:
        return False

    # 4) Control digit ratio
    if digits > len(s) * max_digit_ratio:
        return False

    # 5) Enough "words" (based on spaces)
    if len(s.split()) < min_words:
        return False

    # 6) Ensure majority of chars are "nice": letters/digits/space/basic punct
    allowed = set("abcdefghijklmnopqrstuvwxyz0123456789 .,;:!?\"'()[]{}-_/\\")
    good = sum(ch.lower() in allowed for ch in s)
    if good / len(s) < 0.7:
        return False

    return True
