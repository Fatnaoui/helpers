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


# ---- Arabic-specific helpers ----

# Unicode ranges that cover Arabic script
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


def looks_like_clean_ar_msa(sent: str, min_arabic_ratio: float = 0.5) -> bool:
    """
    Heuristic filter for MSA Arabic sentences.
    - No obvious URLs/hashtags/mentions
    - Not too many digits
    - At least `min_arabic_ratio` of letters are Arabic script.
    """
    s = sent.strip()
    if not s:
        return False

    # 1) Filter out URLs / mentions / hashtags
    if any(token in s for token in ("http://", "https://", "www.", "@", "#")):
        return False

    # 2) Filter out too many digits
    digits = sum(c.isdigit() for c in s)
    if digits > len(s) * 0.3:  # allow a bit more digits in Arabic wiki
        return False

    # 3) Check Arabic vs all letters
    arabic_letters = sum(is_arabic_char(ch) for ch in s)
    all_letters    = sum(ch.isalpha() for ch in s)

    if all_letters == 0:
        return False

    ratio = arabic_letters / all_letters
    if ratio < min_arabic_ratio:
        return False

    return True
