from pathlib import Path

import frontmatter
import mistune
from jinja2 import Environment, FileSystemLoader
from rich import print as rprint

CONTENT_DIR = Path("content")
OUT_DIR = Path("out")
TITLE = "nodata.science"


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
    markdown = mistune.create_markdown(escape=False)

    rprint("# Generating pages from md files...")
    pages = []
    for f in CONTENT_DIR.glob("**/*.md"):
        dst = OUT_DIR / f.relative_to(CONTENT_DIR).with_suffix(".html")
        rprint(f" - '{f}' -> '{dst}'")

        post = frontmatter.load(str(f))
        content = post.content
        metadata = dict(post.metadata)
        metadata["src"] = str(f)
        metadata["dst"] = str(dst)
        metadata["url"] = str(dst.relative_to(OUT_DIR))
        if "/article/" in str(f):
            metadata["is_article"] = True
            validate_blog_metadata(metadata, f)

        pages.append(metadata)

        raw_html = markdown(content)
        template = jinja_env.get_template(metadata.get("_template", "page.html"))
        html = template.render(content=raw_html, **metadata)

        dst.parent.mkdir(exist_ok=True)
        dst.write_text(html)

    rprint("# Generating blog overview page...")
    article_metadata_list = sorted(
        [e for e in pages if "/article/" in str(e)],
        key=lambda e: e["created_at"],
        reverse=True,
    )
    blog_template = jinja_env.get_template("blog.html")
    html = blog_template.render(entries=article_metadata_list)
    dst = OUT_DIR / "blog.html"
    dst.parent.mkdir(exist_ok=True)
    dst.write_text(html)


if __name__ == "__main__":
    main()
