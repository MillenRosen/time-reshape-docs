"""Check real PDF text, links, bookmarks, page sizes and embedded fonts."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import unicodedata

from pypdf import PdfReader


def normalize(value):
    return re.sub(r"\s+", "", unicodedata.normalize("NFKC", value)).replace("\u00ad", "")


def check(path):
    manifest = json.loads(path.with_suffix(".json").read_text())
    reader = PdfReader(path)
    assert not reader.is_encrypted, "The public guide must be readable without a password"
    assert len(reader.pages) == manifest["pages"]
    assert len(reader.pages) > len(manifest["chapters"])
    body_text, fonts, links = [], set(), 0
    for number, page in enumerate(reader.pages, 1):
        assert abs(float(page.mediabox.width) - 595.276) < 1 and abs(float(page.mediabox.height) - 841.89) < 1
        text = page.extract_text()
        assert "\ufffd" not in text, f"Unreadable character on page {number}"
        # WeasyPrint emits running page furniture after the page's body text.
        body = text.rsplit("时光重塑 / 使用手册", 1)[0]
        assert len(normalize(body)) > 65, f"Almost empty page {number}; check the page break"
        body_text.append(body)
        for font_ref in page.get("/Resources", {}).get("/Font", {}).values():
            font = font_ref.get_object()
            if font.get("/Subtype") == "/Type0":
                assert "/ToUnicode" in font, "Missing searchable font mapping"
                font = font["/DescendantFonts"][0].get_object()
            descriptor = font.get("/FontDescriptor")
            assert descriptor and any(key in descriptor for key in ("/FontFile", "/FontFile2", "/FontFile3")), "Font is not embedded"
            fonts.add(str(font.get("/BaseFont")))
        for reference in page.get("/Annots", []):
            annotation = reference.get_object()
            if annotation.get("/Subtype") != "/Link":
                continue
            links += 1
            action = annotation.get("/A", {})
            assert not str(action.get("/URI", "")).startswith("file:"), "Private filesystem link in PDF"
            assert ".trycloudflare.com" not in str(action.get("/URI", "")), "Temporary service link in PDF; rebuild with current release data"
            destination = annotation.get("/Dest", action.get("/D"))
            if isinstance(destination, str):
                assert destination in reader.named_destinations, f"Broken PDF link: {destination}"
    joined = normalize("".join(body_text))
    missing, paragraphs, chapter_pages = [], 0, {}
    for chapter in manifest["chapters"]:
        destination = reader.named_destinations[chapter["id"]]
        chapter_pages[chapter["title"]] = reader.get_destination_page_number(destination) + 1
        for paragraph in chapter["paragraphs"]:
            paragraphs += 1
            if normalize(paragraph) not in joined:
                missing.append(f"{chapter['source']}: {paragraph[:90]}")
    assert not missing, "Missing PDF paragraphs:\n" + "\n".join(missing)
    assert fonts and reader.outline and links > len(manifest["chapters"])
    result = {"pages": len(reader.pages), "chapters": len(manifest["chapters"]),
              "paragraphs_verified": paragraphs, "embedded_fonts": len(fonts),
              "clickable_links": links, "chapter_pages": chapter_pages,
              "a4": True, "searchable_chinese": True, "bytes": path.stat().st_size,
              "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
    print(json.dumps(result, ensure_ascii=False))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    result = check(args.pdf)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
