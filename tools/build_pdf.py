"""Create a paginated Chinese handbook from all pages in the Sphinx navigation."""
import argparse
import hashlib
import html
import json
import logging
from pathlib import Path
import shutil
import subprocess
from urllib.parse import unquote, urljoin, urlsplit

from bs4 import BeautifulSoup
from weasyprint import CSS, HTML
from weasyprint.text.fonts import FontConfiguration


ROOT = Path(__file__).resolve().parents[1]
SITE = "https://time-reshape.readthedocs.io/zh-cn/latest/"


def page_id(path):
    return "page-" + path.removesuffix(".html").replace("/", "--")


def assemble(html_dir, release):
    index = BeautifulSoup((html_dir / "index.html").read_text(), "html.parser")
    paths = ["index.html"]
    for link in index.select(".wy-menu-vertical li.toctree-l1 > a"):
        path = unquote(urlsplit(link["href"]).path)
        if path and path not in paths:
            paths.append(path)
    content_pages = {
        p.relative_to(html_dir).as_posix() for p in html_dir.rglob("*.html")
        if p.name not in {"search.html", "genindex.html"}
    }
    if set(paths) != content_pages:
        raise ValueError(f"Navigation does not cover all content pages: {set(paths) ^ content_pages}")

    chapters, manifest, toc = [], [], []
    for number, path in enumerate(paths, 1):
        soup = BeautifulSoup((html_dir / path).read_text(), "html.parser")
        body = soup.select_one(".document")
        if body is None or body.h1 is None:
            raise ValueError(f"Missing document title: {path}")
        for element in body.select(".headerlink, .toctree-wrapper, .screen-only, script"):
            element.decompose()
        # Image magnification links on the website have no useful print equivalent.
        for link in list(body.select("a.image-reference")):
            link.unwrap()
        title = body.h1.get_text("", strip=True)
        identifier = page_id(path)
        original_text = body.get_text(" ", strip=True)
        for element in body.select("[id]"):
            element["id"] = identifier + "--" + element["id"]
        for image in body.select("img[src]"):
            source = (html_dir / path).parent / unquote(image["src"])
            source = source.resolve()
            if not source.is_relative_to(html_dir) or not source.is_file():
                raise ValueError(f"Missing or external image in {path}: {image['src']}")
            image["src"] = source.as_uri()
            image.attrs.pop("style", None)
        for link in body.select("a[href]"):
            url = urlsplit(link["href"])
            if url.scheme or url.netloc:
                continue
            target = ((html_dir / path).parent / unquote(url.path)).resolve() if url.path else html_dir / path
            if not target.is_relative_to(html_dir):
                raise ValueError(f"Link escapes site: {path}: {link['href']}")
            target_path = target.relative_to(html_dir).as_posix()
            if target_path in paths:
                link["href"] = "#" + page_id(target_path) + ("--" + unquote(url.fragment) if url.fragment else "")
            else:
                link["href"] = urljoin(SITE + path, link["href"])
        # A new chapter is the print equivalent of a web page, preserving its body.
        chapters.append(
            f'<article class="chapter" id="{identifier}">'
            f'<div class="chapter-number">使用指南 / {number:02d}'
            f'<a class="chapter-web" href="{SITE}{path}">在线阅读本章 →</a></div>'
            f'{body.decode_contents()}</article>'
        )
        toc.append(f'<li><a href="#{identifier}"><span class="toc-number">{number:02d}</span>{html.escape(title)}</a></li>')
        manifest.append({"source": path, "title": title, "id": identifier,
                         "text_characters": len(original_text),
                         "text_sha256": hashlib.sha256(original_text.encode()).hexdigest(),
                         "paragraphs": [p.get_text(" ", strip=True) for p in body.select("p")
                                        if len(p.get_text(strip=True)) >= 15]})

    asset = lambda name: (html_dir / "_static/images" / name).as_uri()
    version = html.escape(str(release["version"]))
    book = f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
      <title>时光重塑 · 使用手册 v{version}</title>
      <meta name="description" content="时光重塑完整使用手册：安装、问答、遗迹复原、实时相机与账号指南。">
      </head><body>
      <section class="cover">
        <div class="cover-brand"><img src="{asset('brand-mark.webp')}" alt="时光重塑标志"><span>TIME RESHAPE / 圆圆陪你看园林</span></div>
        <p class="cover-kicker">时光重塑</p><h1>使用手册</h1>
        <p class="cover-subtitle">循迹圆明园，重拾旧时光。</p>
        <img class="cover-landscape" src="{asset('dashuifa.webp')}" alt="圆明园大水法现存遗址">
        <div class="cover-companion"><img src="{asset('yuanyuan.webp')}" alt="圆圆，圆明园记忆精灵">
          <div><p class="cover-greeting">和圆圆一起，<br>从一段史料、一帧影像开始。</p>
          <p>安装与连接 · 史实问答 · 遗迹复原<br>实时相机 · 账号与历史 · 常见问题</p></div></div>
        <div class="cover-edition">ANDROID &amp; WEB <span>v{version} / build {release['build']}</span></div>
      </section>
      <nav class="book-toc" id="book-contents"><p class="eyebrow">阅读导航 / CONTENTS</p><h1>从这里，走进时光。</h1>
        <p>这份手册完整收录网站的 {len(paths)} 个内容页，按阅读顺序整理。<br>点击目录、文内链接或 PDF 书签，可以跳转到相应章节。</p>
        <ol>{''.join(toc)}</ol>
        <div class="reading-note"><strong>留一份手册在身边</strong><p>PDF 可离线阅读、搜索和复制文字。安装包下载、问答与复原仍需要相应网络服务；入口地址和版本信息请以在线手册为准。</p>
        <a href="{SITE}">{SITE}</a></div>
      </nav>{''.join(chapters)}</body></html>'''
    combined = BeautifulSoup(book, "html.parser")
    ids = [e["id"] for e in combined.select("[id]")]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate PDF anchor")
    for link in combined.select('a[href^="#"]'):
        if link["href"][1:] not in ids:
            raise ValueError(f"Unresolved PDF anchor: {link['href']}")
    return book, manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--html-dir", type=Path, default=ROOT / "build/html")
    parser.add_argument("--output", type=Path, default=ROOT / "build/pdf/TimeReshape-User-Guide.pdf")
    parser.add_argument("--copy-to-site", action="store_true")
    parser.add_argument("--keep-html", action="store_true", help="Save print HTML beside the PDF for debugging")
    args = parser.parse_args()
    html_dir = args.html_dir.resolve()
    for family in ("Noto Sans CJK SC", "Noto Serif CJK SC"):
        match = subprocess.check_output(["fc-match", "-f", "%{family}", family], text=True)
        if family not in match:
            raise SystemExit("Install fonts-noto-cjk before building the Chinese PDF.")
    release = json.loads((ROOT / "source/_data/release.json").read_text())
    book, chapters = assemble(html_dir, release)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.keep_html:
        args.output.with_suffix(".html").write_text(book, encoding="utf-8")

    messages = []
    class RenderLog(logging.Handler):
        def emit(self, record):
            messages.append(record.getMessage())
    handler = RenderLog(level=logging.WARNING)
    logger = logging.getLogger("weasyprint")
    logger.addHandler(handler)
    try:
        fonts = FontConfiguration()
        document = HTML(string=book, base_url=html_dir.as_uri() + "/").render(
            stylesheets=[CSS(filename=ROOT / "tools/pdf.css", font_config=fonts)], font_config=fonts)
        if messages:
            raise ValueError("PDF rendering warnings:\n" + "\n".join(messages))
        document.write_pdf(args.output, optimize_images=True, jpeg_quality=92, dpi=180)
    finally:
        logger.removeHandler(handler)
    metadata = {"application_version": release["version"], "pages": len(document.pages),
                "chapters": chapters, "bytes": args.output.stat().st_size,
                "sha256": hashlib.sha256(args.output.read_bytes()).hexdigest()}
    args.output.with_suffix(".json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n")
    if args.copy_to_site:
        destination = html_dir / "_downloads/time-reshape-guide.pdf"
        destination.parent.mkdir(exist_ok=True)
        if args.output.resolve() != destination.resolve():
            shutil.copy2(args.output, destination)
    print(json.dumps({"pdf": str(args.output), "pages": metadata["pages"], "chapters": len(chapters), "bytes": metadata["bytes"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
