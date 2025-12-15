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


# ---- Italian-specific helpers ----

ITALIAN_LETTERS = "abcdefghijklmnopqrstuvwxyzàèéìòù"

def is_mostly_italian_letters_and_punct(s: str, min_ratio: float = 0.7) -> bool:
    """
    Garde les phrases où au moins `min_ratio` des caractères
    sont des lettres (italiennes/latines), espaces ou ponctuation classique.
    """
    allowed = set(ITALIAN_LETTERS + " " + ".,;:!?\"'()[]{}-")
    s_lower = s.lower()
    if not s_lower:
        return False

    good = sum(ch in allowed for ch in s_lower)
    ratio = good / len(s_lower)
    return ratio >= min_ratio


def looks_like_clean_italian(sent: str) -> bool:
    s = sent.strip()
    if not s:
        return False

    # 1) Éviter les URLs / mentions / hashtags
    if any(tok in s for tok in ("http://", "https://", "www.", "@", "#")):
        return False

    # 2) Trop de chiffres → probablement des tableaux / dates / listes
    digits = sum(c.isdigit() for c in s)
    if digits > len(s) * 0.2:  # >20% de chiffres
        return False

    # 3) Majoritairement lettres italiennes + ponctuation
    if not is_mostly_italian_letters_and_punct(s, min_ratio=0.7):
        return False

    return True
