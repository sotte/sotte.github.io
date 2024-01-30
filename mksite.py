"""A very simple static site generator.

metadata with special meaning:

- `_template`: the filename of the template under `templates/` to use to render the given md file
- `_nav_page`: the name of the nav element to highlight

Code rendered with pygments.
"""

import shutil
from pathlib import Path

import frontmatter
import mistune
from jinja2 import Environment, FileSystemLoader
from mistune.directives import Admonition, RSTDirective
from pygments import highlight
from pygments.formatters import html
from pygments.lexers import get_lexer_by_name
from rich import print as rprint


CONTENT_DIR = Path("content")
OUT_DIR = Path("out")
TITLE = "nodata.science"


class _CodeRenderer(mistune.HTMLRenderer):
    def block_code(self, code, info=None):
        if info:
            lexer = get_lexer_by_name(info, stripall=True)
            formatter = html.HtmlFormatter()
            return highlight(code, lexer, formatter)
        return "<pre><code>" + mistune.escape(code) + "</code></pre>"


def validate_blog_metadata(metadata: dict, path: Path):
    errors = []
    for fields in ["title", "created_at", "author"]:
        if fields not in metadata:
            errors.append(f"Missing {fields}")
    if errors:
        errors.insert(0, f"Invalid metadata in {path}:")
        raise ValueError("\n".join(errors))


def main():
    jinja_env = Environment(loader=FileSystemLoader("templates"))
    markdown = mistune.create_markdown(
        escape=False,
        plugins=[
            "strikethrough",
            "footnotes",
            "table",
            "spoiler",
            "url",
            RSTDirective([Admonition()]),
        ],
        renderer=_CodeRenderer(),
    )

    rprint("# Copy static files...")
    for src in (CONTENT_DIR / "static").rglob("**/*"):
        if src.is_dir():
            continue
        dst = OUT_DIR / src.relative_to(CONTENT_DIR)
        rprint(f" - '{src}' -> '{dst}'")
        if dst.exists() and dst.stat().st_mtime > src.stat().st_mtime:
            rprint(f"   - Skipping '{src}'")
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(src, dst)

    rprint("# Generating pages from md files...")
    all_pages = []
    for f in CONTENT_DIR.glob("**/*.md"):
        dst = OUT_DIR / f.relative_to(CONTENT_DIR).with_suffix(".html")
        rprint(f" - '{f}' -> '{dst}'")

        post = frontmatter.load(str(f))
        content = post.content
        metadata = {
            **post.metadata,
            "src": str(f),
            "dst": str(dst),
            "url": str(dst.relative_to(OUT_DIR)),
        }
        if "/article/" in str(f):
            metadata["is_article"] = True
            metadata["_nav_page"] = "blog"
            metadata["_template"] = "article.html"
            validate_blog_metadata(metadata, f)

        all_pages.append(metadata)

        raw_html = markdown(content)
        template = jinja_env.get_template(metadata.get("_template", "page.html"))
        html = template.render(content=raw_html, **metadata)

        dst.parent.mkdir(exist_ok=True)
        dst.write_text(html)

    rprint("# Generating blog overview page...")
    blog_article_metadata_list = sorted(
        [e for e in all_pages if "/article/" in str(e)],
        key=lambda e: e["created_at"],
        reverse=True,
    )
    blog_template = jinja_env.get_template("blog.html")
    html = blog_template.render(entries=blog_article_metadata_list, _nav_page="blog")
    dst = OUT_DIR / "blog.html"
    dst.parent.mkdir(exist_ok=True)
    dst.write_text(html)


if __name__ == "__main__":
    main()
