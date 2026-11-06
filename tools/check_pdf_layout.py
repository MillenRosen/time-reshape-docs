"""Check rendered geometry, including blank fragments invisible to text extraction.

Runs on the pinned WeasyPrint layout tree before writing the PDF, both locally
and on Read the Docs. No application services are involved.
"""
from collections import Counter, defaultdict


def audit_layout(document, source):
    expected = Counter(image['src'] for image in source.select('img[src]'))
    actual = Counter()
    groups = defaultdict(set)
    illustrated = {'app-gallery': 3, 'print-gallery-group': 3,
                   'guide-hero': 2, 'cover-companion': 1}
    decorated = set(illustrated) | {'guide-cards', 'download-panel'}
    group_count = 0
    for number, page in enumerate(document.pages, 1):
        area = page._page_box
        left, top = area.content_box_x(), area.content_box_y()
        right, bottom = left + area.width, top + area.height
        for box in area.descendants():
            element = box.element
            if element is None:
                continue
            kind = type(box).__name__
            if element.tag == 'img' and hasattr(box, 'replacement'):
                actual[element.get('src')] += 1
                x, y = box.border_box_x(), box.border_box_y()
                assert box.width > 0 and box.height > 0, f'Invisible image on page {number}'
                assert x >= left-1 and y >= top-1 and x+box.border_width() <= right+1 and y+box.border_height() <= bottom+1, f'Image outside printable area on page {number}'
            classes = set(element.get('class', '').split())
            marked = classes & decorated
            if not marked or kind not in {'BlockBox', 'FlexBox'}:
                continue
            # Inline/line boxes inherit the element but are not container fragments.
            key = id(element)
            groups[key].add(number)
            descendants = list(box.descendants())
            images = sum(child.element is not None and child.element.tag == 'img' and hasattr(child, 'replacement') for child in descendants)
            text = ''.join(getattr(child, 'text', '') for child in descendants).strip()
            assert images or text, f'Empty decorated fragment {marked} on page {number}'
            for name in marked & illustrated.keys():
                assert images == illustrated[name], f'Split image group {name} on page {number}: {images} images'
            if 'print-gallery-group' in marked:
                assert any(child.element is not None and child.element.tag in {'h2', 'h3'} for child in descendants), f'Gallery heading detached on page {number}'
            group_count += 1
    assert actual == expected, f'Missing or duplicated images: expected {sum(expected.values())}, rendered {sum(actual.values())}'
    assert all(len(pages) == 1 for pages in groups.values()), 'Decorated group split across pages'
    return {'pages_checked': len(document.pages), 'image_instances': sum(actual.values()),
            'decorated_groups': group_count, 'empty_fragments': 0,
            'split_image_groups': 0, 'images_outside_printable_area': 0}
