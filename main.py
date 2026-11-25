#!/usr/bin/env python3
"""Entry for make.fun bounty u-puan-describe-your-ex-in-one-word-9fc6ebe7.

Brief: describe your ex in a single word, at most 111 characters,
with nothing else attached.

This program prints exactly that one word to stdout and nothing else.
All validation, diagnostics and verification go to stderr (or nowhere),
so stdout stays byte-identical to the entry text plus a trailing newline.

Entry text: Unforgettable
Character count: 13 (limit 111)
Word count: 1
"""

import re
import sys


# ---------------------------------------------------------------------------
# Entry definition
# ---------------------------------------------------------------------------

ENTRY_TEXT = "Unforgettable"

# The brief's hard limits, kept as named constants so they are easy to audit.
MAX_LENGTH = 111
MAX_WORDS = 1

# Fallback candidates, in preference order. Each one must itself satisfy the
# brief, so a fallback can never produce an invalid entry. The primary entry
# is listed first on purpose: the normal path never reaches a fallback.
FALLBACK_WORDS = (
    "Unforgettable",
    "Memorable",
    "Bittersweet",
)

# A single word for this brief means letters only: no spaces, no punctuation,
# no digits, no hyphen, no underscore. Anything else would risk being read
# as more than one word or as extra attached content.
_SINGLE_WORD_RE = re.compile(r"^[A-Za-z]+$")

# Control characters and other invisible characters must never appear in
# the output, because they would be extra content beyond the single word.
_CONTROL_RE = re.compile(r"[\x00-\x1f\x7f]")


# ---------------------------------------------------------------------------
# Character and word helpers
# ---------------------------------------------------------------------------

def count_characters(text):
    """Return the number of characters in ``text``.

    The brief counts characters, not bytes, so a plain ``len`` is correct
    here. The entry is plain ASCII, so the two agree anyway.
    """
    return len(text)


def count_words(text):
    """Return the number of whitespace-separated words in ``text``."""
    stripped = text.strip()
    if not stripped:
        return 0
    return len(stripped.split())


def has_whitespace(text):
    """Return True if ``text`` contains any whitespace character."""
    return any(char.isspace() for char in text)


def has_control_character(text):
    """Return True if ``text`` contains a control character."""
    return bool(_CONTROL_RE.search(text))


def is_plain_ascii(text):
    """Return True if every character in ``text`` is plain ASCII.

    The entry is meant to be a single readable English word. Rejecting
    non-ASCII characters keeps the output unambiguous across systems and
    prevents an accented or invisible character from sneaking in as extra
    content beyond the one word.
    """
    try:
        text.encode("ascii")
    except UnicodeEncodeError:
        return False
    return True


def has_punctuation_or_digits(text):
    """Return True if ``text`` contains punctuation, digits or symbols."""
    return any(not char.isalpha() for char in text)


def is_single_word(text):
    """Return True if ``text`` is exactly one plain alphabetic word."""
    if not isinstance(text, str):
        return False
    if not text:
        return False
    if text != text.strip():
        return False
    if has_whitespace(text):
        return False
    if has_control_character(text):
        return False
    if not is_plain_ascii(text):
        return False
    if has_punctuation_or_digits(text):
        return False
    return bool(_SINGLE_WORD_RE.match(text))


def describe_entry(text):
    """Return a small audit dictionary describing ``text``.

    This is used only for internal verification. It is never printed to
    stdout, so it cannot pollute the entry output.
    """
    return {
        "text": text,
        "characters": count_characters(text),
        "words": count_words(text),
        "is_single_word": is_single_word(text),
        "within_limit": count_characters(text) <= MAX_LENGTH,
    }


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate_entry(text):
    """Validate ``text`` against every rule in the brief.

    Returns a list of human-readable problems. An empty list means the
    text is a valid entry.
    """
    problems = []
    if not isinstance(text, str):
        problems.append("entry is not a string")
        return problems
    if not text:
        problems.append("entry is empty")
    if text != text.strip():
        problems.append("entry has leading or trailing whitespace")
    if has_whitespace(text):
        problems.append("entry contains whitespace (more than one word)")
    if has_control_character(text):
        problems.append("entry contains a control character")
    if not is_plain_ascii(text):
        problems.append("entry contains non-ASCII characters")
    if has_punctuation_or_digits(text):
        problems.append("entry contains punctuation, digits or symbols")
    if count_words(text) != MAX_WORDS:
        problems.append(
            "entry must be exactly one word, found %d words"
            % count_words(text)
        )
    if not is_single_word(text):
        problems.append("entry must be a single alphabetic word")
    if count_characters(text) > MAX_LENGTH:
        problems.append(
            "entry is %d characters, over the %d-character limit"
            % (count_characters(text), MAX_LENGTH)
        )
    return problems


def choose_entry():
    """Choose the entry text: the primary word, or the first valid fallback.

    The primary word is expected to validate cleanly. Fallbacks exist only
    so that a typo or bad edit in the primary can never produce invalid
    output: the program would rather print a different valid word than an
    invalid one.
    """
    candidates = [ENTRY_TEXT] + list(FALLBACK_WORDS)
    seen = set()
    for candidate in candidates:
        if candidate in seen:
            continue
        seen.add(candidate)
        if not validate_entry(candidate):
            return candidate
    # Every candidate is validated at authoring time, so reaching this point
    # would mean the source itself is broken. Fail loudly on stderr and
    # refuse to print anything to stdout rather than emit a bad entry.
    raise ValueError("no valid single-word entry available")


# ---------------------------------------------------------------------------
# Output verification
# ---------------------------------------------------------------------------

def verify_output(output, expected):
    """Check that ``output`` is exactly the expected entry plus a newline.

    Returns a list of problems; an empty list means the output is exact.
    This runs before anything is written to real stdout, using the string
    that is about to be emitted.
    """
    problems = []
    if output != expected + "\n":
        problems.append("output does not match the expected entry exactly")
    if output.count("\n") != 1:
        problems.append("output must contain exactly one trailing newline")
    if output.strip() != expected:
        problems.append("output stripped content differs from the entry")
    if not is_single_word(output.strip()):
        problems.append("output is not a single word")
    return problems


def emit_entry(text):
    """Write ``text`` followed by a single newline to stdout, exactly once."""
    output = text + "\n"
    problems = verify_output(output, text)
    if problems:
        for problem in problems:
            print("error: %s" % problem, file=sys.stderr)
        raise SystemExit(1)
    sys.stdout.write(output)
    sys.stdout.flush()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    """Validate the entry, then print exactly that word to stdout."""
    try:
        entry = choose_entry()
    except ValueError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 1
    problems = validate_entry(entry)
    if problems:
        for problem in problems:
            print("error: %s" % problem, file=sys.stderr)
        return 1
    audit = describe_entry(entry)
    if not audit["is_single_word"] or not audit["within_limit"]:
        print("error: entry failed final audit", file=sys.stderr)
        return 1
    emit_entry(entry)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
