"""Apply final page-order, terminology and numeric-notation consistency."""
import fitz
from palette import DEEP_GRAY, DEEP_NAVY, OFF_WHITE, WHITE


GREY = OFF_WHITE
NAVY = DEEP_NAVY
BODY = DEEP_GRAY

TITLES = [
    "Simpaisa Network Playbook",
    "The playbook at a glance",
    "Contents",
    "Simpaisa and our network",
    "How businesses use Simpaisa",
    "How payments move through Simpaisa",
    "The Gap We Close",
    "Seven markets going digital",
    "Pakistan",
    "Bangladesh",
    "Nepal",
    "Iraq",
    "Egypt",
    "Saudi Arabia",
    "Nigeria",
    "Acceptance across the network",
    "Remittance receive markets",
    "Connecting a merchant to the network",
    "Let's connect more markets.",
]


def _font_key(name):
    if "Poppins" in name:
        return "PH"
    if "Semi" in name or "Bold" in name:
        return "IB"
    return "IR"


def _color(value):
    return tuple(((value >> shift) & 255) / 255 for shift in (16, 8, 0))


def _wrap(font, text, size, width):
    lines = []
    current = ""
    for word in text.split():
        candidate = (current + " " + word).strip()
        if font.text_length(candidate, fontsize=size) <= width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def rebuild_navigation(doc):
    doc.set_toc([[1, title, page_number] for page_number, title in enumerate(TITLES, 1)])
    contents = doc[2]
    doc.xref_set_key(contents.xref, "Annots", "null")
    for target_page, title in enumerate(TITLES[3:], 3):
        matches = contents.search_for(title)
        if not matches:
            raise ValueError(("contents title missing", title))
        for rect in matches:
            contents.insert_link({"kind": fitz.LINK_GOTO, "from": rect, "page": target_page, "to": fitz.Point(0, 0)})


def apply(doc, H):
    fonts = {
        "IR": fitz.Font(fontfile=str(H / "fonts" / "Inter.ttf")),
        "IB": fitz.Font(fontfile=str(H / "fonts" / "InterSemi.ttf")),
        "PH": fitz.Font(fontfile=str(H / "fonts" / "Poppins.ttf")),
    }
    for page in doc:
        for key, filename in [("IR", "Inter.ttf"), ("IB", "InterSemi.ttf"), ("PH", "Poppins.ttf")]:
            page.insert_font(fontname=key, fontfile=str(H / "fonts" / filename))

    queued = []

    def add(page_number, rect, text, size, font="IR", color=BODY, fill=None, leading=None):
        queued.append(
            {
                "page": page_number - 1,
                "rect": fitz.Rect(rect),
                "text": text,
                "size": size,
                "font": font,
                "color": color,
                "fill": fill,
                "leading": leading or size * 1.3,
            }
        )

    add(2, (165, 204, 540, 235), "Founded in 2016 and headquartered in Singapore. PCI DSS Level 1 and ISO 27001 certified; 100+ merchants across 10+ use cases.", 9.6, fill=WHITE, leading=13)
    add(2, (165, 252, 540, 281), "Pakistan, Bangladesh, Nepal, Iraq, Egypt, Saudi Arabia and Nigeria. Together, their 2025 population is about 900m.", 9.6, fill=WHITE, leading=13)
    add(3, (39, 72, 556, 101), "How to read this playbook: start with the network, compare the seven markets, then review acceptance, remittance payout and merchant onboarding.", 9.2, fill=GREY, leading=13)
    add(3, (99, 258, 500, 272), "Payment methods, market scale and Simpaisa coverage across seven markets.", 7.6, fill=WHITE)
    add(3, (99, 277, 500, 294), "Seven markets going digital", 9.6, "PH", NAVY, WHITE)
    add(3, (99, 293, 520, 307), "Population, internet use, mobile connections and digital payment growth across seven markets.", 7.6, fill=WHITE)
    for rect, text in [
        ((99, 363, 400, 376), "Raast, wallets and PayPak; full service coverage."),
        ((99, 398, 430, 411), "MFS wallets, Bangla QR and NPSB; full service coverage."),
        ((99, 432, 405, 445), "Wallets, QR and connectIPS; full service coverage."),
        ((99, 501, 410, 514), "Wallets, InstaPay and Meeza; full service coverage."),
        ((99, 570, 390, 583), "NIP, wallets and Verve; full service coverage."),
    ]:
        add(3, rect, text, 7.6, fill=WHITE)
    add(13, (49, 630, 230, 647), "Full service coverage", 9, color=WHITE, fill=NAVY)
    add(8, (39, 437, 556, 463), "Source: World Bank and ITU. Mobile connections are subscriptions, not unique people. Bar scales differ by column.", 7, color=(.32, .39, .50), fill=GREY, leading=9)

    # Use the same explicitly dated population series as page 8.
    add(9, (39, 104, 556, 143), "Pakistan has 255.2m people (2025) and 161m broadband subscriptions. In Jan-Mar 2026, digital channels accounted for 92% of retail payments. Local wallets and Raast give customers payment options through accounts they already use.", 8.4, color=WHITE, fill=False, leading=11.2)
    add(10, (39, 104, 556, 151), "Bangladesh has 175.7m people (2025) and 136m internet subscriptions. MFS providers held 250.2m registered accounts at December 2025 and processed BDT 18.7tn (about USD 152bn) during 2025. bKash and Nagad provide established wallet checkout options.", 8.4, color=WHITE, fill=False, leading=11.2)
    add(11, (39, 104, 556, 151), "Nepal has 29.6m people (2025) and 31m broadband subscriptions. At July 2025, it had 26.8m wallet users and 27.7m mobile-banking users. QR payment value reached NPR 958bn (about USD 7bn) in FY2024/25, up from NPR 500bn a year earlier.", 8.4, color=WHITE, fill=False, leading=11.2)
    add(14, (39, 104, 556, 143), "Saudi Arabia has 37.0m people (2025). In 2025, electronic payments accounted for 85% of retail payments. mada is the domestic card scheme and sarie supports instant bank transfers. Simpaisa supports mada, sarie, stc bank and urpay.", 8.4, color=WHITE, fill=False, leading=11.2)
    add(15, (39, 104, 556, 151), "Nigeria has 237.5m people (2025) and 157m internet subscriptions. NIP processed 11.2bn transfers worth NGN 1,070tn (about USD 725bn) in 2024. Simpaisa connects businesses to local wallets, bank transfers and cards, with domestic settlement in naira.", 8.4, color=WHITE, fill=False, leading=11.2)
    add(17, (478, 349, 550, 383), "Wallet or bank account", 7.4, color=BODY, fill=(245 / 255, 245 / 255, 245 / 255), leading=10)

    for item in queued:
        doc[item["page"]].add_redact_annot(item["rect"], fill=item["fill"], cross_out=False)
    for page_index in sorted({item["page"] for item in queued}):
        doc[page_index].apply_redactions(images=0, graphics=0, text=0)
    for item in queued:
        page = doc[item["page"]]
        rect = item["rect"]
        lines = _wrap(fonts[item["font"]], item["text"], item["size"], rect.width)
        for line_index, line in enumerate(lines):
            page.insert_text(
                (rect.x0, rect.y0 + fonts[item["font"]].ascender * item["size"] + line_index * item["leading"]),
                line,
                fontname=item["font"],
                fontsize=item["size"],
                color=item["color"],
            )

    # A plus sign marks growth or a lower-bound count. A greater-than sign marks a service threshold.
    threshold_map = {
        "markets with all three flows": "markets with full service coverage",
        "All three flows": "Full service coverage",
        "Multi-rail, above 99.9% uptime": "Multi-rail, >99.9% uptime",
        "Above 80%": ">80%",
        "Above 96%": ">96%",
        "Above 98.5%": ">98.5%",
        "Above 99%": ">99%",
    }
    replacements = []
    for page_index, page in enumerate(doc):
        page_dict = page.get_text("dict")
        spans = [span for block in page_dict["blocks"] for line in block.get("lines", []) for span in line["spans"]]
        for old, new in threshold_map.items():
            for rect in page.search_for(old):
                span = next((s for s in spans if fitz.Rect(s["bbox"]).intersects(rect)), None)
                if span is None:
                    raise ValueError((page_index + 1, old, "style not found"))
                replacements.append(
                    (page_index, rect, new, span["size"], _font_key(span["font"]), _color(span["color"]))
                )
                page.add_redact_annot(rect, fill=False, cross_out=False)
    for page_index in sorted({item[0] for item in replacements}):
        doc[page_index].apply_redactions(images=0, graphics=0, text=0)
    for page_index, rect, new, size, font, color in replacements:
        baseline = rect.y0 + fonts[font].ascender * size
        doc[page_index].insert_text((rect.x0, baseline), new, fontname=font, fontsize=size, color=color)

    rebuild_navigation(doc)
