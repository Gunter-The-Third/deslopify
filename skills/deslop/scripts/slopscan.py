#!/usr/bin/env python3
"""slopscan: count AI-prose tells per 1,000 words.

Reads Markdown, LaTeX, reStructuredText and plain text. For each feature it
reports a rate per 1,000 prose words and compares it with a ceiling. The
ceiling comes from a baseline of the author's own earlier writing when one is
given, and from rough built-in values otherwise.

Most of the signal is structural (em dashes, colon reveals, semicolons,
"not X but Y"). Word lists catch far less. The counts are leads for a reader
to check. A colon that introduces a list, or a "not X but Y" that separates
two claims a reader could confuse, is legitimate.

Standard library only. Python 3.8+.
"""
from __future__ import annotations

import argparse
import bisect
import html
import json
import re
import statistics
import sys
from dataclasses import dataclass, field
from pathlib import Path

PROSE_EXTS = {".md", ".markdown", ".mdx", ".txt", ".rst", ".tex"}
SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "build", "dist",
             "__pycache__", ".tox", "site-packages", "vendor", "_build"}

# name: (description, built-in ceiling per 1k words, measure_only without a baseline)
FEATURES = {
    "em_dash": ("em dashes, and spaced en dashes or double hyphens used as dashes", 1.0, False),
    "colon_reveal": ("mid-sentence colon followed by a clause that restates or reveals", 1.0, False),
    "semicolon": ("semicolons joining two clauses", 1.5, False),
    "negation_parallel": ("'not X but Y', 'X, not Y', 'it's not X, it's Y', 'rather than'", 1.0, False),
    "signposting": ("announcing instead of saying: 'it is worth noting', 'here's why', 'in summary'", 0.5, False),
    "stock_lexicon": ("stock vocabulary: delve, leverage, robust, seamless, pivotal, crucial ...", 0.5, False),
    "intensifier": ("empty intensifiers: very, truly, significantly, incredibly ...", 3.0, False),
    "hedge_stack": ("sentences carrying two or more different hedges", 1.0, False),
    "transition_opener": ("sentences opening with Moreover, Furthermore, Additionally ...", 1.0, False),
    "copula_avoidance": ("'serves as', 'stands as', 'boasts' where 'is' or 'has' works", 0.3, False),
    "bold_lead_in": ("Markdown lines or bullets that open with a bold label", 3.0, False),
    "rhetorical_q": ("short rhetorical question answered in the next sentence", 0.3, False),
    "fragment": ("one- and two-word sentences, and three-word ones like 'That's it.'", 1.0, False),
    "exclamation": ("exclamation marks", 0.5, False),
    "emoji": ("emoji in prose", 0.5, False),
    "tricolon": ("lists of three ('X, Y and Z'); measured only unless a baseline is given", 2.0, True),
}

WORD_RE = re.compile(r"[A-Za-z\u00C0-\u024F][A-Za-z\u00C0-\u024F'\u2019-]*|\d+(?:[.,]\d+)*")

EM_DASH_RE = re.compile(r"\u2014|(?<=\s)--(?=\s)|(?<=\s)\u2013(?=\s)")

_BE = r"(?:is|are|was|were|does|do|did)"
_PRON = r"(?:it|this|that|they|he|she)(?:[\u2019']s|[\u2019']re|\s+is|\s+are|\s+was)"
NEGATION_RES = [re.compile(p, re.I) for p in (
    r"\bnot\s+(?:just|only|merely|simply|so much)\b[^.?!;]{0,100}?\bbut\b",
    r"\b" + _BE + r"n[\u2019']?t\b[^.?!;]{1,80}?[,;:\u2014]\s*" + _PRON + r"\b",
    r"\b" + _BE + r"\s+not\b[^.?!;]{1,80}?[,;:\u2014]\s*" + _PRON + r"\b",
    r"\b(?:it|this|that)(?:[\u2019']s|\s+is|\s+was)\s+not\b[^.?!]{1,80}[.!]\s+(?:it|this|that)(?:[\u2019']s|\s+is|\s+was)\b",
    r"\bnot\b[^.?!;,]{1,60}\s+but\s",
    r",\s+not\s+[^,.;:?!]{1,50}(?=[.?!;])",
    r"\brather than\b",
    r"\bless\s+(?:about\s+)?[^.?!;]{1,40}?\band more\b",
)]

SIGNPOST_RE = re.compile(
    r"\b(?:it(?:[\u2019']s| is) worth (?:noting|mentioning|pointing out|highlighting)"
    r"|worth noting|it(?:[\u2019']s| is) important to (?:note|remember|understand|recogni[sz]e)"
    r"|it should be noted|here[\u2019']s (?:the thing|why|what|how|the kicker|the catch|the deal)"
    r"|here is (?:why|what|how)"
    r"|let[\u2019']s (?:dive|take a (?:closer )?look|break (?:it|this) down|explore|unpack|walk through)"
    r"|let us (?:now )?(?:turn|consider|examine|explore)"
    r"|in this (?:section|article|post|guide|document|chapter),? (?:we|i|you)\b"
    r"|the (?:key|main|short|real|big) (?:takeaway|insight|answer|point|thing|idea) (?:is|here)"
    r"|the bottom line|in summary|in conclusion|to summari[sz]e|to sum up|in short,|overall,"
    r"|as (?:mentioned|noted|discussed|stated) (?:earlier|above|previously|before)"
    r"|needless to say|at the end of the day|it goes without saying|without further ado"
    r"|buckle up|first and foremost|last but not least|that said,|that being said|with that (?:said|in mind))",
    re.I)

STOCK_RE = re.compile(
    r"\b(?:delve[sd]?|delving|tapestry|testament|realm|landscape|multifaceted|holistic|nuanced"
    r"|seamless(?:ly)?|robust(?:ly|ness)?|leverag(?:e|es|ed|ing)|utili[sz](?:e|es|ed|ing|ation)"
    r"|underscor(?:e|es|ed|ing)|pivotal|paramount|crucial(?:ly)?|vital|foster(?:s|ed|ing)?"
    r"|elevat(?:e|es|ing)|unlock(?:s|ed|ing)?|empower(?:s|ed|ing)?|streamlin(?:e|es|ed|ing)"
    r"|game[- ]?changer|cutting[- ]edge|ever[- ](?:evolving|changing)|intricate|intricacies"
    r"|meticulous(?:ly)?|showcas(?:e|es|ed|ing)|embark(?:s|ed|ing)?|vibrant|bustling"
    r"|synerg(?:y|ies|istic)|paradigm|transformative|myriad|plethora|commendable|noteworthy"
    r"|invaluable|harness(?:es|ed|ing)?|resonat(?:e|es|ed|ing)|comprehensive|insightful|nestled"
    r"|navigat(?:e|es|ing) the|in today[\u2019']s (?:[a-z-]+ )?world"
    r"|plays? an? (?:crucial|pivotal|key|vital|critical|significant|important) role"
    r"|shed(?:s|ding)? light on|in the realm of|due to the fact that|serves? to)\b",
    re.I)

INTENSIFIER_RE = re.compile(
    r"\b(?:very|really|truly|incredibly|extremely|highly|significantly|substantially|remarkably"
    r"|deeply|fundamentally|essentially|absolutely|genuinely|undeniably|undoubtedly|profoundly"
    r"|immensely|exceptionally|blazing(?:ly)?)\b", re.I)

HEDGE_RE = re.compile(
    r"\b(?:may|might|could|potentially|possibly|perhaps|arguably|somewhat|likely|generally"
    r"|typically|presumably|conceivably|in some cases|to some extent|tends? to|appears? to"
    r"|seems? to|relatively)\b", re.I)

TRANSITION_RE = re.compile(
    r"^[\"'\u201c(]*(?:Moreover|Furthermore|Additionally|In addition|Ultimately|In essence"
    r"|Notably|Importantly|Crucially|Interestingly|Indeed|Consequently|Essentially)\b")

COPULA_RE = re.compile(
    r"\b(?:serves?|served|serving|stands?|stood|functions?|acts?|acted) as\b|\bboasts?\b", re.I)

TRICOLON_RE = re.compile(
    r"\b[\w'-]+(?:\s+[\w'-]+){0,2},\s+[\w'-]+(?:\s+[\w'-]+){0,2},?\s+(?:and|or)\s+[\w'-]+")

QUOTE_RE = re.compile(r"\u201c[^\u201d]*\u201d|\"[^\"]*\"")

# Text just before a colon that makes it a label rather than a reveal.
LABEL_COLON_RE = re.compile(
    r"(?:\b(?:Figure|Fig|Table|Algorithm|Listing|Equation|Eq|Step|Example|Appendix|Chapter|Section)\.?\s*[\dA-Z][\d.]*"
    r"|(?<![\w.])\d+(?:\.\d+)*|\b(?:by|in|url|doi|date|signed|isbn|issn|email|tel|phone|re|cc|to|from|subject|author|authors|supervisors?|keywords|source))$",
    re.I)

# Three-word sentences that lean on the previous one ("That's it.", "It is.").
FRAGMENT_RE = re.compile(r"(?:that|this|it)(?:[\u2019']s|\s+is|\s+was)\b|(?:just|simply|no|not|exactly)\b", re.I)

EMOJI_RE = re.compile("[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U00002B50\U00002705]")

# Abbreviations that end in a full stop without ending the sentence.
ABBREV_RE = re.compile(
    r"(?:\b(?:e\.g|i\.e|etc|et al|vs|cf|Fig|Figs|Eq|Eqs|Sec|Ch|No|Dr|Mr|Mrs|Ms|Prof|approx"
    r"|resp|viz|al)\.|\b[A-Z]\.)$")
SPLIT_RE = re.compile(r"(?<=[.!?])[\"'\u201d\u2019)\]]*\s+(?=[A-Z0-9\"'\u201c\u2018(\[])")


# ------------------------------------------------------------------ parsing

@dataclass
class Paragraph:
    text: str
    offsets: list = field(default_factory=list)  # char offset where each source line starts
    lines: list = field(default_factory=list)    # matching source line numbers

    def line(self, pos: int) -> int:
        return self.lines[max(0, bisect.bisect_right(self.offsets, pos) - 1)]


MD_LIST_RE = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+")
MD_BOLD_LEAD_RE = re.compile(
    r"^(\s*(?:(?:[-*+]|\d+[.)])\s+)?)(\*\*|__)(?:(?!\2).){1,80}?(?:\2\s*[:.\u2014\u2013-]|[:.]\s*\2)")


def _md_inline(s: str) -> str:
    s = re.sub(r"`[^`]*`", "CODE", s)
    s = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", s)
    s = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", s)
    s = re.sub(r"\[([^\]]*)\]\[[^\]]*\]", r"\1", s)
    s = re.sub(r"<https?://[^>]+>", "URL", s)
    s = re.sub(r"https?://\S+", "URL", s)
    s = re.sub(r"<[^>]+>", "", s)
    s = re.sub(r"(\*\*|__)(.+?)\1", r"\2", s)
    s = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"\1", s)
    s = re.sub(r"(?<!\w)_(?!\s)(.+?)(?<!\s)_(?!\w)", r"\1", s)
    return html.unescape(s)


def clean_markdown(lines):
    """Return ([(lineno, text or None)], [line-level hits]). None marks a paragraph break."""
    out, extra = [], []
    in_front = bool(lines) and lines[0].strip() == "---"
    in_fence, fence, in_comment = False, "", False
    for i, raw in enumerate(lines, 1):
        s = raw.rstrip("\n")
        st = s.strip()
        if in_front:
            if i > 1 and st in ("---", "..."):
                in_front = False
            out.append((i, None))
            continue
        if in_fence:
            if st.startswith(fence):
                in_fence = False
            out.append((i, None))
            continue
        m = re.match(r"(`{3,}|~{3,})", st)
        if m:
            in_fence, fence = True, m.group(1)
            out.append((i, None))
            continue
        if in_comment:
            if "-->" not in s:
                out.append((i, None))
                continue
            in_comment, s = False, s.split("-->", 1)[1]
        s = re.sub(r"<!--.*?-->", "", s)
        if "<!--" in s:
            s, in_comment = s.split("<!--")[0], True
        st = s.strip()
        if not st or st.startswith(("#", "|", ">")) or re.fullmatch(r"[-*_=]{3,}", st):
            out.append((i, None))
            continue
        bm = MD_BOLD_LEAD_RE.match(s)
        if bm:
            extra.append(("bold_lead_in", i, st[:160]))
            s = bm.group(1) + s[bm.end():]  # drop the label so its colon is not counted again
        if MD_LIST_RE.match(s):
            out.append((i, None))
            s = MD_LIST_RE.sub("", s, count=1)
        out.append((i, _md_inline(s)))
    return out, extra


TEX_SKIP_ENVS = {
    "equation", "align", "gather", "multline", "eqnarray", "displaymath", "math", "flalign",
    "figure", "table", "tabular", "tabularx", "longtable", "verbatim", "lstlisting", "minted",
    "algorithm", "algorithmic", "algorithm2e", "tikzpicture", "comment", "thebibliography",
}
TEX_BEGIN_RE = re.compile(r"\\begin\{([a-zA-Z0-9]+)\*?\}")
TEX_END_RE = re.compile(r"\\end\{([a-zA-Z0-9]+)\*?\}")
TEX_HEADING_RE = re.compile(
    r"\\(?:part|chapter|section|subsection|subsubsection|paragraph|subparagraph|caption)\*?\s*(?:\[[^\]]*\])?\{")


def _strip_braced(s: str, start: int) -> str:
    """Remove the command starting at s[start:] whose argument opens at the first '{'."""
    j, depth = s.index("{", start), 0
    for k in range(j, len(s)):
        if s[k] == "{":
            depth += 1
        elif s[k] == "}":
            depth -= 1
            if depth == 0:
                return s[:start] + " " + s[k + 1:]
    return s[:start]


def _tex_inline(s: str) -> str:
    s = s.replace("---", "\u2014").replace("--", "\u2013")
    s = re.sub(r"\$\$.*?\$\$", "X", s)
    s = re.sub(r"(?<!\\)\$(?:\\\$|[^$])*?(?<!\\)\$", "X", s)
    s = re.sub(r"\\\(.*?\\\)", "X", s)
    s = re.sub(r"\\\[.*?\\\]", "X", s)
    s = re.sub(r"\\[a-zA-Z]*cite[a-zA-Z]*\*?(?:\[[^\]]*\]){0,2}\{[^}]*\}", "", s)
    s = re.sub(r"\\(?:ref|eqref|cref|Cref|autoref|pageref|vref)\*?\{[^}]*\}", "1", s)
    s = re.sub(r"\\label\{[^}]*\}", "", s)
    s = re.sub(r"\\href\{[^}]*\}\{([^}]*)\}", r"\1", s)
    s = re.sub(r"\\url\{[^}]*\}", "URL", s)
    s = s.replace("\\\\", " ").replace("~", " ")
    s = re.sub(r"\\([%&$#_{}])", r"\1", s)
    s = re.sub(r"\\[a-zA-Z@]+\*?(?:\[[^\]]*\])?", "", s)
    s = s.replace("{", "").replace("}", "")
    return s.replace("``", "\u201c").replace("''", "\u201d")


def clean_latex(lines):
    out = []
    has_doc = any("\\begin{document}" in ln for ln in lines)
    in_doc = not has_doc
    skip_depth, in_display = 0, False
    for i, raw in enumerate(lines, 1):
        s = re.sub(r"(?<!\\)%.*", "", raw.rstrip("\n"))
        if not in_doc:
            if "\\begin{document}" in s:
                in_doc = True
            out.append((i, None))
            continue
        if "\\end{document}" in s:
            in_doc = False
            out.append((i, None))
            continue
        if skip_depth:
            skip_depth += sum(1 for m in TEX_BEGIN_RE.finditer(s) if m.group(1) in TEX_SKIP_ENVS)
            skip_depth -= sum(1 for m in TEX_END_RE.finditer(s) if m.group(1) in TEX_SKIP_ENVS)
            skip_depth = max(skip_depth, 0)
            out.append((i, None))
            continue
        if in_display:
            if "\\]" in s:
                in_display, s = False, s.split("\\]", 1)[1]
            else:
                out.append((i, None))
                continue
        opened = [m.group(1) for m in TEX_BEGIN_RE.finditer(s) if m.group(1) in TEX_SKIP_ENVS]
        if opened:
            closed = [m.group(1) for m in TEX_END_RE.finditer(s) if m.group(1) in TEX_SKIP_ENVS]
            skip_depth = max(len(opened) - len(closed), 0)
            out.append((i, None))
            continue
        if "\\[" in s and "\\]" not in s.split("\\[", 1)[1]:
            s, in_display = s.split("\\[", 1)[0], True
        hm = TEX_HEADING_RE.search(s)
        if hm:
            out.append((i, None))
            s = _strip_braced(s, hm.start())
        if TEX_BEGIN_RE.search(s) or TEX_END_RE.search(s) or "\\item" in s:
            out.append((i, None))
            s = re.sub(r"\\item(?:\[[^\]]*\])?", " ", s)
        s = _tex_inline(s)
        out.append((i, s if s.strip() else None))
        if in_display:
            out.append((i, None))
    return out, []


def clean_plain(lines, rst=False):
    out = []
    for i, raw in enumerate(lines, 1):
        s = raw.rstrip("\n")
        st = s.strip()
        if rst and (st.startswith("..") or re.fullmatch(r"([=\-~^\"'`#*+])\1{2,}", st)):
            out.append((i, None))
            continue
        out.append((i, s if st else None))
    return out, []


def paragraphs(cleaned):
    paras, text, offsets, lines = [], "", [], []
    for lineno, t in cleaned + [(0, None)]:
        if t is None or not t.strip():
            if text.strip():
                paras.append(Paragraph(text, offsets, lines))
            text, offsets, lines = "", [], []
            continue
        if text:
            text += " "
        offsets.append(len(text))
        lines.append(lineno)
        text += re.sub(r"\s+", " ", t.strip())
    return paras


def sentences(text: str):
    out, start = [], 0
    for m in SPLIT_RE.finditer(text):
        chunk = text[start:m.start()]
        if ABBREV_RE.search(chunk.rstrip("\"'\u201d\u2019)]")):
            continue
        out.append((start, chunk))
        start = m.end()
    out.append((start, text[start:]))
    return [(o, s.strip()) for o, s in out if s.strip()]


# ---------------------------------------------------------------- detection

@dataclass
class Hit:
    feature: str
    path: str
    line: int
    snippet: str


def _snippet(text, a, b, width=60):
    lo, hi = max(0, a - width), min(len(text), b + width)
    s = text[lo:hi].strip()
    return ("..." if lo > 0 else "") + s + ("..." if hi < len(text) else "")


def _merged(regexes, text):
    spans = sorted((m.start(), m.end()) for r in regexes for m in r.finditer(text))
    out, last = [], -1
    for a, b in spans:
        if a >= last:
            out.append((a, b))
            last = b
    return out


def detect(p: Paragraph, path: str):
    hits, t = [], p.text
    quoted = [(m.start(), m.end()) for m in QUOTE_RE.finditer(t)]

    def add(feature, a, b, snippet=None):
        if snippet is None and any(qa <= a < qb for qa, qb in quoted):
            return  # quoted words are a mention, not the author's own prose
        hits.append(Hit(feature, path, p.line(a), snippet or _snippet(t, a, b)))

    for m in EM_DASH_RE.finditer(t):
        add("em_dash", m.start(), m.end())

    for m in re.finditer(r"(?<=\S):(?=\s)", t):
        after = t[m.end():]
        if not after.strip() or after.lstrip()[:1] in "•*-–":
            continue  # colon introduces a list or block
        pre = t[:m.start()]
        if LABEL_COLON_RE.search(pre):
            continue  # caption, algorithm step, form field or citation label
        if (pre.count("“") > pre.count("”") or pre.count('"') % 2
                or pre.count("(") > pre.count(")")):
            continue  # inside a quoted title or a parenthesis
        rest = re.split(r"[.!?](?:\s|$)", after, maxsplit=1)[0]
        if len(WORD_RE.findall(rest)) < 3:
            continue
        if rest.count(",") >= 2 or ";" in rest:
            continue  # an enumeration
        add("colon_reveal", m.start(), m.end())

    for m in re.finditer(";", t):
        pre = t[:m.start()]
        if pre.count("(") > pre.count(")") or pre.count("[") > pre.count("]"):
            continue  # citation lists and parentheticals
        if t[m.end():].strip():
            add("semicolon", m.start(), m.end())

    for feature, regexes in (("negation_parallel", NEGATION_RES), ("signposting", [SIGNPOST_RE]),
                             ("stock_lexicon", [STOCK_RE]), ("intensifier", [INTENSIFIER_RE]),
                             ("copula_avoidance", [COPULA_RE]), ("tricolon", [TRICOLON_RE]),
                             ("emoji", [EMOJI_RE])):
        for a, b in _merged(regexes, t):
            add(feature, a, b)

    sents = sentences(t)
    lengths = []
    for idx, (off, s) in enumerate(sents):
        n = len(WORD_RE.findall(s))
        if n:
            lengths.append(n)
        whole = s if len(s) <= 200 else s[:197] + "..."
        if TRANSITION_RE.match(s):
            add("transition_opener", off, off + len(s), whole)
        if len({m.group(0).lower() for m in HEDGE_RE.finditer(s)}) >= 2:
            add("hedge_stack", off, off + len(s), whole)
        if s.endswith("?") and n <= 6 and idx < len(sents) - 1:
            add("rhetorical_q", off, off + len(s), whole + " " + sents[idx + 1][1][:80])
        if len(sents) > 1 and s[-1:] in ".!" and re.search(r"[A-Za-z]{2}", s) and (0 < n <= 2 or (n == 3 and FRAGMENT_RE.match(s))):
            add("fragment", off, off + len(s), whole)
        if s.rstrip("\"'\u201d\u2019)").endswith("!"):
            add("exclamation", off, off + len(s), whole)
    return hits, lengths


@dataclass
class Scan:
    files: list = field(default_factory=list)
    words: int = 0
    lengths: list = field(default_factory=list)
    hits: list = field(default_factory=list)

    def counts(self):
        c = {f: 0 for f in FEATURES}
        for h in self.hits:
            c[h.feature] += 1
        return c

    def rates(self):
        k = 1000.0 / max(self.words, 1)
        return {f: n * k for f, n in self.counts().items()}

    def sentence_stats(self):
        if len(self.lengths) < 5:
            return None, None
        mean = statistics.mean(self.lengths)
        return mean, statistics.pstdev(self.lengths) / mean


def scan_text(text: str, suffix: str, path: str = "<text>", scan: Scan | None = None) -> Scan:
    scan = scan or Scan()
    lines = text.splitlines()
    suffix = suffix.lower()
    if suffix == ".txt" and re.search(r"\\(?:documentclass|begin\{document\}|section\{)", text):
        suffix = ".tex"  # LaTeX source saved as .txt
    if suffix == ".tex":
        cleaned, extra = clean_latex(lines)
    elif suffix in (".md", ".markdown", ".mdx"):
        cleaned, extra = clean_markdown(lines)
    else:
        cleaned, extra = clean_plain(lines, rst=suffix == ".rst")
    scan.files.append(path)
    for feature, line, snip in extra:
        scan.hits.append(Hit(feature, path, line, snip))
    for p in paragraphs(cleaned):
        scan.words += len(WORD_RE.findall(p.text))
        hits, lengths = detect(p, path)
        scan.hits.extend(hits)
        scan.lengths.extend(lengths)
    return scan


def iter_files(paths):
    for raw in paths:
        p = Path(raw)
        if p.is_dir():
            for f in sorted(p.rglob("*")):
                if f.is_file() and f.suffix.lower() in PROSE_EXTS and not (set(f.parts) & SKIP_DIRS):
                    yield f
        elif p.is_file():
            yield p
        else:
            print(f"slopscan: no such file or directory: {raw}", file=sys.stderr)


def scan_paths(paths) -> Scan:
    scan = Scan()
    for f in iter_files(paths):
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
        except OSError as e:
            print(f"slopscan: cannot read {f}: {e}", file=sys.stderr)
            continue
        scan_text(text, f.suffix, str(f), scan)
    return scan


# --------------------------------------------------------------- baselines

def baseline_from_scan(scan: Scan, sources) -> dict:
    mean, cv = scan.sentence_stats()
    return {"sources": [str(s) for s in sources], "words": scan.words,
            "rates": {f: round(r, 4) for f, r in scan.rates().items()},
            "sentence_mean": mean, "sentence_cv": cv}


def load_baseline(paths) -> dict | None:
    if not paths:
        return None
    if len(paths) == 1 and paths[0].endswith(".json"):
        return json.loads(Path(paths[0]).read_text())
    return baseline_from_scan(scan_paths(paths), paths)


# One hit in a short file is not a pattern. A feature needs this many hits to count.
MIN_HITS = 2


def assess(scan: Scan, baseline: dict | None):
    """Return per-feature rows and the total excess over ceilings per 1k words."""
    rows, excess_total = [], 0.0
    counts, rates = scan.counts(), scan.rates()
    for f, (desc, ref, measure_only) in FEATURES.items():
        rate = rates[f]
        if baseline is not None:
            b = baseline["rates"].get(f, 0.0)
            ceiling = max(2 * b, b + 0.5)
            if rate > ceiling:
                status = "HIGH"
            elif b >= 0.5 and rate < 0.5 * b:
                status = "below baseline: leave alone"
            else:
                status = "ok"
            excess = max(0.0, rate - ceiling)
            shown_ref = b
        else:
            ceiling, shown_ref = ref, ref
            if measure_only:
                status, excess = "measured only", 0.0
            else:
                status = "HIGH" if rate > ceiling else "ok"
                excess = max(0.0, rate - ceiling)
        if counts[f] < MIN_HITS and status == "HIGH":
            status, excess = f"ok (under {MIN_HITS} hits)", 0.0
        excess_total += excess
        rows.append({"feature": f, "hits": counts[f], "rate": rate, "reference": shown_ref,
                     "ceiling": ceiling, "status": status, "excess": excess, "description": desc})
    return rows, excess_total


def excess(scan: Scan, baseline: dict | None = None) -> float:
    return assess(scan, baseline)[1]


# --------------------------------------------------------------------- CLI

def report(scan: Scan, baseline: dict | None, show_list: bool, only: set | None,
           compact: bool = False) -> str:
    rows, total = assess(scan, baseline)
    out = []
    src = (f"baseline: {', '.join(baseline['sources'])} ({baseline['words']:,} words)"
           if baseline else "no baseline: built-in ceilings")
    out.append(f"slopscan: {len(scan.files)} file(s), {scan.words:,} prose words, "
               f"{len(scan.lengths):,} sentences ({src})")
    if scan.words < 300:
        out.append("note: under 300 words, so rates are noisy. Read the hits, not the rates.")
    if compact:
        out.append(f"excess over ceilings: {total:.2f} per 1k words")
        for r in rows:
            if r["hits"] and (not only or r["feature"] in only):
                out.append(f"{r['feature']}: {r['hits']} hits, {r['rate']:.2f}/1k, {r['status']}")
        locations = {}
        for hit in scan.hits:
            if not only or hit.feature in only:
                locations.setdefault((hit.path, hit.line), set()).add(hit.feature)
        for (path, line), features in sorted(locations.items()):
            out.append(f"{path}:{line}  [{', '.join(sorted(features))}]")
        return "\n".join(out)
    out.append("")
    ref_label = "base" if baseline else "ceil"
    out.append(f"{'feature':<19} {'hits':>5} {'per 1k':>7} {ref_label:>6}  status")
    for r in rows:
        out.append(f"{r['feature']:<19} {r['hits']:>5} {r['rate']:>7.2f} {r['reference']:>6.2f}  {r['status']}")
    mean, cv = scan.sentence_stats()
    if mean is not None:
        line = f"\nsentence length: mean {mean:.1f} words, CV {cv:.2f}"
        if baseline and baseline.get("sentence_cv"):
            line += f" (baseline mean {baseline['sentence_mean']:.1f}, CV {baseline['sentence_cv']:.2f})"
        out.append(line)
    out.append(f"excess over ceilings: {total:.2f} per 1k words")
    if show_list:
        out.append("")
        hits = [h for h in scan.hits if not only or h.feature in only]
        for h in sorted(hits, key=lambda h: (h.path, h.line, h.feature)):
            out.append(f"{h.path}:{h.line}  [{h.feature}]  {h.snippet}")
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Count AI-prose tells per 1,000 words.")
    ap.add_argument("paths", nargs="+", help="files or directories (.md .tex .txt .rst)")
    ap.add_argument("--baseline", nargs="+", metavar="PATH",
                    help="the author's earlier writing (files/dirs), or a saved baseline .json")
    ap.add_argument("--save-baseline", metavar="OUT.json",
                    help="scan PATHS as the author's own writing and save their rates as a baseline")
    ap.add_argument("--list", action="store_true", help="print every hit with file:line")
    ap.add_argument("--compact", action="store_true",
                    help="show nonzero features and grouped file:line hits without snippets")
    ap.add_argument("--feature", action="append", choices=sorted(FEATURES),
                    help="with --list or --compact, show only this feature (repeatable)")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--fail-above", type=float, metavar="X",
                    help="exit 1 when the excess over ceilings exceeds X per 1k words")
    args = ap.parse_args(argv)

    scan = scan_paths(args.paths)
    if args.save_baseline:
        data = baseline_from_scan(scan, args.paths)
        Path(args.save_baseline).write_text(json.dumps(data, indent=2) + "\n")
        print(f"saved baseline from {scan.words:,} words to {args.save_baseline}")
        if scan.words < 5000:
            print("warning: under 5,000 words; a baseline this small is unreliable.")
        return 0

    baseline = load_baseline(args.baseline)
    rows, total = assess(scan, baseline)
    if args.json:
        mean, cv = scan.sentence_stats()
        print(json.dumps({"files": scan.files, "words": scan.words, "sentences": len(scan.lengths),
                          "sentence_mean": mean, "sentence_cv": cv, "excess": total,
                          "baseline": baseline and {k: baseline[k] for k in ("sources", "words")},
                          "features": rows,
                          "hits": [h.__dict__ for h in scan.hits]}, indent=2))
    else:
        print(report(scan, baseline, args.list, set(args.feature or []), compact=args.compact))
    if args.fail_above is not None and total > args.fail_above:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
