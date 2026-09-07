"""Left-align the closing brand and headings while preserving the office map."""
from io import BytesIO

import fitz
from PIL import Image, ImageDraw
from palette import BRIGHT_BLUE, WHITE


def _svg_pdf(path):
    svg = fitz.open(stream=path.read_bytes(), filetype="svg")
    return fitz.open(stream=svg.convert_to_pdf(), filetype="pdf")


def apply(doc, H):
    source = fitz.open(stream=doc.tobytes(), filetype="pdf")
    original = source[18]
    pix = original.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
    old = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    clean = Image.new("RGB", old.size)
    draw = ImageDraw.Draw(clean)
    sample_y = min(180, old.height - 1)
    for x in range(old.width):
        draw.line((x, 0, x, old.height), fill=old.getpixel((x, sample_y)))
    stream = BytesIO()
    clean.save(stream, format="PNG", optimize=True)

    closing_doc = fitz.open()
    page = closing_doc.new_page(width=595, height=842)
    page.insert_image(page.rect, stream=stream.getvalue())
    for name, filename in [("IR", "Inter.ttf"), ("IB", "InterSemi.ttf"), ("PH", "Poppins.ttf")]:
        page.insert_font(fontname=name, fontfile=str(H / "fonts" / filename))

    logo = _svg_pdf(H.parent / "assets" / "simpaisa-0ddcd8e522.svg")
    page.show_pdf_page(fitz.Rect(40, 42, 180, 81.14), logo, 0)
    page.insert_text((40, 402), "Let's connect", fontname="PH", fontsize=37, color=WHITE)
    page.insert_text((40, 450), "more markets.", fontname="PH", fontsize=37, color=WHITE)
    page.insert_text((40, 647), "Our office locations", fontname="IR", fontsize=12, color=WHITE)
    page.insert_image(
        fitz.Rect(40, 660, 555, 778),
        filename=str(H.parent / "assets" / "office-locations-print-4x-52214d4291.png"),
        keep_proportion=True,
    )
    page.draw_line((40, 794), (555, 794), color=tuple(channel * 0.62 + 0.38 for channel in BRIGHT_BLUE), width=0.55)
    website = fitz.Rect(40, 801, 185, 821)
    page.insert_text((40, 816), "www.simpaisa.com", fontname="PH", fontsize=15, color=WHITE)
    page.insert_text((552, 816), "19", fontname="IR", fontsize=8, color=WHITE)
    page.insert_link({"kind": fitz.LINK_URI, "from": website, "uri": "https://www.simpaisa.com/"})

    target = doc[18]
    target.add_redact_annot(target.rect, fill=False, cross_out=False)
    target.apply_redactions(images=1, graphics=2, text=0)
    target.show_pdf_page(target.rect, closing_doc, 0)
