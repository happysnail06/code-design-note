"""Generate the Docusaurus docs/ tree from the two source markdown documents.

Purpose: split the single knowledge document into one page per topic, grouped by section, and add the
merged coding convention as the last page of the sidebar.
Usage: python3 scripts/split_knowledge.py <knowledge.md> <convention.md> <docs_dir>
"""

import json
import os
import re
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path

# Folder name and sidebar label of each detail section
SECTIONS = {
    "A": ("a-repo-structure", "A. 프로젝트 구성과 실행 흐름"),
    "B": ("b-code-structure", "B. 인터페이스와 객체 설계"),
    "C": ("c-language-features", "C. decorator와 언어 기능"),
    "D": ("d-failure-handling", "D. 실패에 대비하는 방법"),
}

# URL slug of each topic; the page title itself comes from the source heading
TOPIC_SLUGS = {
    "A1": "adapter-upstream", "A2": "lazy-import", "A3": "entry-point", "A4": "validate-first",
    "A5": "source-paths", "A6": "repo-docs",
    "B1": "abc-protocol", "B2": "template-method", "B3": "registry", "B4": "mixin", "B5": "proxy",
    "B6": "callable", "B7": "context-state",
    "C1": "dataclass", "C2": "namedtuple", "C3": "property", "C4": "classmethod", "C5": "staticmethod",
    "C6": "abstract-method", "C7": "context-manager", "C8": "cache", "C9": "init-subclass", "C10": "mapping",
    "C11": "base-exception", "C12": "small-features",
    "D1": "atomic-replace", "D2": "directory-swap", "D3": "reversible-order", "D4": "nonblocking-lock",
    "D5": "resume-check", "D6": "format-version", "D7": "upstream-check", "D8": "retry-classes",
    "D9": "result-check",
}

TOPIC_REF = re.compile(r"\b([A-E](?:1[0-2]|[1-9]))\b")


@dataclass
class Topic:
    """One detail topic, such as A1, and where its page is written."""

    topic_id: str
    title: str
    body: str
    path: Path
    description: str = field(init=False)

    def __post_init__(self) -> None:
        # The first paragraph after the heading is the one-sentence description of the topic
        if not (paragraph := self.body.strip().split("\n\n", 1)[0].strip()) or paragraph.startswith("#"):
            raise ValueError(f"topic {self.topic_id} has no description paragraph under its heading")
        self.description = " ".join(paragraph.split())


def section_between(text: str, start: str, end: str | None) -> str:
    """Return the text from heading `start` up to heading `end`.

    Purpose: cut one top-level part of the knowledge document by its exact heading line.
    Args:
        text: full knowledge markdown.
        start: heading line that opens the part.
        end: heading line that opens the next part, or None for the end of the document.
    Returns:
        The part without its opening heading and without trailing horizontal rules.
    Raises:
        ValueError: if either heading is missing.
    """
    # Both headings must exist, otherwise the split would silently drop or merge text
    if (begin := text.find("\n" + start + "\n")) < 0:
        raise ValueError(f"knowledge document has no heading {start!r}")
    finish = len(text)
    if end is not None and (finish := text.find("\n" + end + "\n", begin + 1)) < 0:
        raise ValueError(f"knowledge document has no heading {end!r}")
    body = text[begin + len(start) + 2:finish]
    return re.sub(r"(\n-{3,}\s*)+$", "\n", body.rstrip() + "\n")


def outside_code(markdown: str, transform) -> str:
    """Apply `transform` only to prose, leaving fenced blocks and inline code untouched.

    Purpose: rewrite topic references in running text without touching code samples.
    Args:
        markdown: page markdown.
        transform: function from a prose fragment to its rewritten form.
    Returns:
        The markdown with every prose fragment transformed.
    """
    out = []
    # Fenced blocks are kept verbatim
    for n, block in enumerate(re.split(r"(^```.*?^```)", markdown, flags=re.S | re.M)):
        if n % 2:
            out.append(block)
            continue
        # Inline code spans inside prose are kept verbatim too
        parts = re.split(r"(`[^`\n]+`)", block)
        out.append("".join(part if i % 2 else transform(part) for i, part in enumerate(parts)))
    return "".join(out)


def link_topics(markdown: str, page: Path, topics: dict[str, Topic], e_page: Path) -> str:
    """Turn topic ids such as "B4" in prose into links to that topic's page.

    Purpose: let readers jump between related topics.
    Args:
        markdown: page markdown.
        page: path of the page being written, for relative links.
        topics: every topic by id.
        e_page: path of the "설계할 때 주의할 점" page, the target of "[E]"-style references.
    Returns:
        The markdown with known topic ids linked; unknown ids are left as text.
    """
    def relative(target: Path) -> str:
        return os.path.relpath(target, page.parent).replace(os.sep, "/")

    def replace(match: re.Match) -> str:
        topic = topics.get(match.group(1))
        return f"[{match.group(1)}]({relative(topic.path)})" if topic else match.group(0)

    def transform(prose: str) -> str:
        # Overview items such as "**[A1] Adapter와 upstream**" become one link named after the topic
        prose = re.sub(r"\*\*\[([A-E](?:1[0-2]|[1-9]))\] ([^*\n]+)\*\*",
                       lambda m: f"**[{m.group(1)}. {m.group(2)}]({relative(topics[m.group(1)].path)})**", prose)
        # Any other bracketed id only needs its link target
        prose = re.sub(r"\[([A-E](?:1[0-2]|[1-9]))\](?!\()",
                       lambda m: f"[{m.group(1)}]({relative(topics[m.group(1)].path)})", prose)
        return re.sub(r"(?<!\[)" + TOPIC_REF.pattern + r"(?!\])", replace, prose)

    return outside_code(markdown, transform)


def promote(markdown: str) -> str:
    """Raise every heading outside code blocks by one level ("### x" becomes "## x")."""
    return outside_code(markdown, lambda prose: re.sub(r"^#(#{2,}) ", r"\1 ", prose, flags=re.M))


def front_matter(**fields: object) -> str:
    """Render Docusaurus front matter; values are JSON-quoted so any text is safe."""
    lines = [f"{key}: {json.dumps(value, ensure_ascii=False)}" for key, value in fields.items()]
    return "---\n" + "\n".join(lines) + "\n---\n\n"


def main(argv: list[str] | None = None) -> int:
    knowledge_path, convention_path, docs_arg = argv or sys.argv[1:]
    text = "\n" + Path(knowledge_path).read_text()
    docs = Path(docs_arg)

    # Cut the knowledge document into its top-level parts
    title_match = re.match(r"\n# (.+)\n", text)
    if title_match is None:
        raise ValueError("knowledge document must start with a '# ' title")
    intro = re.sub(r"(\n-{3,}\s*)+$", "\n", text[title_match.end():text.find("\n## 1. ")].rstrip() + "\n")
    # These parts sat under a "##" heading in the single file; as pages their sub-headings move up one level
    concepts = promote(section_between(text, "## 1. 먼저 알아 둘 개념", "## 2. 한눈에 보기"))
    overview = promote(section_between(text, "## 2. 한눈에 보기", "## 3. 상세 분석"))
    detail = section_between(text, "## 3. 상세 분석", None)

    # Split the detail part into sections A-E, then each section into its topics
    section_bodies = dict(re.findall(r"^### ([A-E])\. [^\n]+\n(.*?)(?=^### [A-E]\. |\Z)", detail, re.S | re.M))
    if sorted(section_bodies) != ["A", "B", "C", "D", "E"]:
        raise ValueError(f"expected detail sections A-E, found {sorted(section_bodies)}")
    topics: dict[str, Topic] = {}
    section_intros: dict[str, str] = {}
    for letter, (folder, _) in SECTIONS.items():
        body = section_bodies[letter]
        first = re.search(r"^#### ", body, re.M)
        section_intros[letter] = body[:first.start()] if first else body
        for topic_id, title, topic_body in re.findall(
            r"^#### ([A-E]\d{1,2})\. ([^\n]+)\n(.*?)(?=^#### |\Z)", body, re.S | re.M
        ):
            if topic_id not in TOPIC_SLUGS:
                raise ValueError(f"topic {topic_id} has no slug in TOPIC_SLUGS")
            path = docs / folder / f"{topic_id.lower()}-{TOPIC_SLUGS[topic_id]}.md"
            topics[topic_id] = Topic(topic_id, title, topic_body, path)
    if missing := sorted(set(TOPIC_SLUGS) - set(topics)):
        raise ValueError(f"slugs exist for topics missing from the document: {missing}")

    # Start from an empty docs tree so removed topics do not linger
    if docs.exists():
        shutil.rmtree(docs)
    e_page = docs / "e-not-to-follow.md"

    def write(path: Path, markdown: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(markdown.rstrip() + "\n")

    # Top pages
    write(docs / "intro.md", front_matter(slug="/", sidebar_position=1, sidebar_label="개요")
          + f"# {title_match.group(1)}\n" + link_topics(intro, docs / "intro.md", topics, e_page))
    write(docs / "concepts.md", front_matter(sidebar_position=2, sidebar_label="먼저 알아 둘 개념")
          + "# 먼저 알아 둘 개념\n" + link_topics(concepts, docs / "concepts.md", topics, e_page))
    write(docs / "overview.md", front_matter(sidebar_position=3, sidebar_label="한눈에 보기")
          + "# 한눈에 보기\n" + link_topics(overview, docs / "overview.md", topics, e_page))

    # One folder per section: an index page with the section intro and topic list, then one page per topic
    for position, (letter, (folder, label)) in enumerate(SECTIONS.items(), start=4):
        write(docs / folder / "_category_.json",
              json.dumps({"label": label, "position": position, "collapsed": False}, ensure_ascii=False, indent=2)
              + "\n")
        index_path = docs / folder / "index.md"
        members = [t for t in topics.values() if t.topic_id.startswith(letter)]
        listing = "\n".join(
            f"- **[{t.topic_id}. {t.title}]({t.path.name})**: {t.description}" for t in members
        )
        write(index_path, front_matter(sidebar_position=0, sidebar_label="이 절의 주제")
              + f"# {label}\n\n" + link_topics(section_intros[letter].strip() + "\n", index_path, topics, e_page)
              + "\n## 주제\n\n" + listing + "\n")
        for order, topic in enumerate(members, start=1):
            # Topic sub-sections (#####) become the page's h2 sections
            body = re.sub(r"^##### ", "## ", topic.body, flags=re.M)
            write(topic.path, front_matter(sidebar_position=order, sidebar_label=f"{topic.topic_id}. {topic.title.replace('`', '')}",
                                           description=topic.description)
                  + f"# {topic.title}\n" + link_topics(body, topic.path, topics, e_page))

    # Section E is a single page, and the merged convention is the last page of the sidebar
    cautions = outside_code(
        section_bodies["E"].strip(),
        lambda prose: re.sub(r"^#### ", "## ", prose, flags=re.M),
    )
    write(e_page, front_matter(sidebar_position=8, sidebar_label="E. 설계할 때 주의할 점")
          + "# E. 설계할 때 주의할 점\n\n" + link_topics(cautions + "\n", e_page, topics, e_page))
    write(docs / "coding-convention.md", front_matter(sidebar_position=99, sidebar_label="코딩 규약")
          + Path(convention_path).read_text())

    print(f"wrote {len(topics)} topic pages, 4 section indexes, and 5 top pages into {docs}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
