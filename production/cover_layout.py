"""Rebuild the cover using the approved left-aligned reference hierarchy."""
from io import BytesIO

import fitz
from PIL import Image, ImageDraw
from palette import BRIGHT_BLUE, DEEP_NAVY, WHITE


NAVY = DEEP_NAVY
PALE_BLUE = tuple(channel * 0.62 + 0.38 for channel in BRIGHT_BLUE)


def _svg_pdf(path):
    svg = fitz.open(stream=path.read_bytes(), filetype="svg")
    return fitz.open(stream=svg.convert_to_pdf(), filetype="pdf")


def apply(doc, H):
    source = fitz.open(stream=doc.tobytes(), filetype="pdf")
    original = source[0]

    # Preserve the approved landmark artwork while removing the old embedded title.
    pix = original.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
    old = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    clean = Image.new("RGB", old.size)
    draw = ImageDraw.Draw(clean)
    sample_x = min(16, old.width - 1)
    for y in range(old.height):
        draw.line((0, y, old.width, y), fill=old.getpixel((sample_x, y)))
    artwork_top = round(600 * pix.height / original.rect.height)
    # Keep the landmark panorama but exclude the inherited footer so the new
    # divider, title and website appear exactly once.
    artwork_bottom = round(783 * pix.height / original.rect.height)
    clean.paste(old.crop((0, artwork_top, old.width, artwork_bottom)), (0, artwork_top))
    stream = BytesIO()
    clean.save(stream, format="PNG", optimize=True)

    cover_doc = fitz.open()
    page = cover_doc.new_page(width=595, height=842)
    page.insert_image(page.rect, stream=stream.getvalue())
    for name, filename in [("IR", "Inter.ttf"), ("IB", "InterSemi.ttf"), ("PH", "Poppins.ttf")]:
        page.insert_font(fontname=name, fontfile=str(H / "fonts" / filename))

    logo = _svg_pdf(H.parent / "assets" / "simpaisa-0ddcd8e522.svg")
    page.show_pdf_page(fitz.Rect(40, 46, 180, 85.14), logo, 0)
    page.insert_text((40, 288), "2026", fontname="IR", fontsize=11, color=WHITE)
    page.insert_text((40, 337), "Simpaisa Network Playbook", fontname="PH", fontsize=32, color=WHITE)
    page.insert_text((40, 385), "Local Payment Networks Across Emerging Markets", fontname="IR", fontsize=16, color=WHITE)
    page.draw_line((40, 432), (92, 432), color=PALE_BLUE, width=1.6)
    page.draw_line((40, 794), (555, 794), color=(0.50, 0.68, 0.93), width=0.55)
    page.insert_text((40, 814), "SIMPAISA NETWORK PLAYBOOK", fontname="IR", fontsize=7.5, color=WHITE)
    website = fitz.Rect(450, 802, 555, 819)
    page.insert_text((450, 814), "www.simpaisa.com", fontname="IR", fontsize=7.5, color=WHITE)
    page.insert_link({"kind": fitz.LINK_URI, "from": website, "uri": "https://www.simpaisa.com/"})

    target = doc[0]
    target.add_redact_annot(target.rect, fill=False, cross_out=False)
    target.apply_redactions(images=1, graphics=2, text=0)
    target.show_pdf_page(target.rect, cover_doc, 0)
