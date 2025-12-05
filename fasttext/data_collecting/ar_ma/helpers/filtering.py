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


# ---------- Arabic script helpers (same base as MSA) ----------

ARABIC_RANGES = [
    (0x0600, 0x06FF),  # Arabic
    (0x0750, 0x077F),  # Arabic Supplement
    (0x08A0, 0x08FF),  # Arabic Extended-A
    (0xFB50, 0xFDFF),  # Arabic Presentation Forms-A
    (0xFE70, 0xFEFF),  # Arabic Presentation Forms-B
]

def is_arabic_char(ch: str) -> bool:
    code = ord(ch)
    return any(start <= code <= end for start, end in ARABIC_RANGES)


def looks_like_clean_ar_ma(sent: str,
                           min_arabic_ratio: float = 0.4) -> bool:
    """
    Heuristic filter for Moroccan Arabic (Darija) in Arabic script.
    - Rejects URLs / hashtags / mentions
    - Rejects very digit-heavy lines
    - Requires that a good share of letters are Arabic script
      (but allows some Latin letters due to code-switching).
    """
    s = sent.strip()
    if not s:
        return False

    # 1) Filter out URLs / mentions / hashtags
    if any(token in s for token in ("http://", "https://", "www.", "@", "#")):
        return False

    # 2) Reject sentences with too many digits (tables, dates lists, etc.)
    digits = sum(c.isdigit() for c in s)
    if digits > len(s) * 0.3:  # allow up to 30% digits
        return False

    # 3) Check proportion of Arabic letters among all letters (Arabic + Latin)
    arabic_letters = sum(is_arabic_char(ch) for ch in s)
    latin_letters  = sum('a' <= ch.lower() <= 'z' for ch in s)
    all_letters    = arabic_letters + latin_letters

    if all_letters == 0:
        return False

    ratio = arabic_letters / all_letters
    if ratio < min_arabic_ratio:
        # if less than 40% of letters are Arabic, probably not pure ar_ma script
        return False

    return True
