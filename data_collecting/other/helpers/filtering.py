
import unicodedata
import re

# Unicode ranges per script
SCRIPT_RANGES = {
    "ru": [  # Cyrillic
        (0x0400, 0x04FF),
    ],
    "zh": [  # CJK Unified Ideographs (very rough but good enough)
        (0x4E00, 0x9FFF),
    ],
    "hi": [  # Devanagari
        (0x0900, 0x097F),
    ],
    "he": [  # Hebrew
        (0x0590, 0x05FF),
    ],
}

# Minimum ratio of chars that must belong to the script
SCRIPT_MIN_RATIO = {
    "ru": 0.40,  # Russian often mixes digits/latin; 40% is reasonable
    "zh": 0.50,  # Chinese: usually a lot of Han chars
    "hi": 0.50,
    "he": 0.50,
}


INVISIBLE_CATEGORIES = {"Cf", "Cc"}  # format & control chars


def remove_invisible_chars(s: str) -> str:
    """
    Remove weird / invisible Unicode chars and normalize spaces.
    """
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


def looks_like_clean_generic(
    sent: str,
    min_words: int = 3,
    max_digit_ratio: float = 0.7,
) -> bool:
    """
    Very generic filter for ANY language:
    - no URLs / hashtags / mentions
    - not too many digits
    - at least `min_words` tokens
    """
    s = sent.strip()
    if not s:
        return False

    # 1) remove obvious junk
    if any(tok in s for tok in ("http://", "https://", "www.", "@", "#")):
        return False

    # 2) avoid numeric-heavy garbage
    digits = sum(c.isdigit() for c in s)
    if digits > len(s) * max_digit_ratio:
        return False

    # 3) min words
    if len(s.split()) < min_words:
        return False

    return True


def sentence_split(text: str):
    """
    Simple sentence splitter that works ok for many languages:
    split on . ! ? followed by whitespace.
    (Only for OTHER_LATIN here.)
    """
    return re.split(r'(?<=[\.\!\?])\s+', text)

def _in_ranges(ch: str, ranges) -> bool:
    cp = ord(ch)
    for start, end in ranges:
        if start <= cp <= end:
            return True
    return False


def script_ratio(text: str, lang: str) -> float:
    """
    Approximate ratio of characters that belong to the expected script
    for a given language code (ru, zh, hi, he).
    """
    ranges = SCRIPT_RANGES.get(lang)
    if not ranges:
        # If we don't know the script, say ratio = 1.0 (no filtering)
        return 1.0

    script_count = 0
    relevant_count = 0

    for ch in text:
        # Skip spaces
        if ch.isspace():
            continue

        cat = unicodedata.category(ch)
        # Skip punctuation and symbols, focus on letters/digits
        if cat.startswith("P") or cat.startswith("S"):
            continue

        relevant_count += 1
        if _in_ranges(ch, ranges):
            script_count += 1

    if relevant_count == 0:
        return 0.0

    return script_count / relevant_count

def is_mostly_lang_script(text: str, lang: str) -> bool:
    ratio = script_ratio(text, lang)
    min_ratio = SCRIPT_MIN_RATIO.get(lang, 0.0)
    return ratio >= min_ratio


