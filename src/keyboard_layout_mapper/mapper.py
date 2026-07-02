"""Text mapping between Persian and English keyboard layouts."""

BASE_EN_TO_FA = {
    "`": "پ",
    "q": "ض",
    "w": "ص",
    "e": "ث",
    "r": "ق",
    "t": "ف",
    "y": "غ",
    "u": "ع",
    "i": "ه",
    "o": "خ",
    "p": "ح",
    "[": "ج",
    "]": "چ",
    "a": "ش",
    "s": "س",
    "d": "ی",
    "f": "ب",
    "g": "ل",
    "h": "ا",
    "j": "ت",
    "k": "ن",
    "l": "م",
    ";": "ک",
    "'": "گ",
    "z": "ظ",
    "x": "ط",
    "c": "ز",
    "v": "ر",
    "b": "ذ",
    "n": "د",
    "m": "ئ",
    ",": "و",
    "?": "؟",
    "0": "۰",
    "1": "۱",
    "2": "۲",
    "3": "۳",
    "4": "۴",
    "5": "۵",
    "6": "۶",
    "7": "۷",
    "8": "۸",
    "9": "۹",
}

EN_TO_FA = dict(BASE_EN_TO_FA)
for english_letter in "abcdefghijklmnopqrstuvwxyz":
    EN_TO_FA[english_letter.upper()] = EN_TO_FA[english_letter]

FA_TO_EN = {persian: english for english, persian in BASE_EN_TO_FA.items()}
FA_TO_EN.update({"ي": "d", "ك": ";", "آ": "h", "ؤ": "c", "إ": "h", "أ": "h", "ة": "m"})


def map_text(text: str) -> str:
    """Convert text between Persian and English layouts.

    Auto-detects direction based on which layout has more matching characters.
    """
    english_matches = sum(1 for char in text if char in EN_TO_FA)
    persian_matches = sum(1 for char in text if char in FA_TO_EN)
    mapping = FA_TO_EN if persian_matches > english_matches else EN_TO_FA
    return "".join(mapping.get(char, char) for char in text)
