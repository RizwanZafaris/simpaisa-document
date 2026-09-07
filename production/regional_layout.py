"""Render country pages as native PDF content with aligned Option 3 method lanes.

Copy approved service text from the preceding build. Only layout is changed.
Fresh page streams avoid the inherited clipping stacks of the edited source PDF.
"""
from io import BytesIO
import json
import fitz
from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from palette import BRIGHT_BLUE, DEEP_NAVY, DEEP_GRAY, LIGHT_GRAY, WHITE


METHODS = {
    'Pakistan': [
        ['JazzCash', 'easypaisa', 'Alfa', 'ZINDIGI', 'HBL Konnect'],
        ['Raast', '1LINK IBFT', 'PayPak', 'Visa', 'Mastercard']],
    'Bangladesh': [
        ['bKash', 'Nagad', 'Rocket', 'Upay'],
        ['Bangla QR', 'NPSB', 'Visa', 'Mastercard', 'American Express']],
    'Nepal': [
        ['eSewa', 'Khalti', 'IME Pay'],
        ['connectIPS', 'NEPALPAY QR', 'NEPALPAY Card', 'Visa', 'Mastercard']],
    'Iraq': [
        ['ZainCash', 'AsiaHawala', 'FastPay', 'NassPay'],
        ['IRPSI', 'Visa', 'Mastercard']],
    'Egypt': [
        ['Vodafone Cash', 'e& Cash', 'Orange Cash', 'WE Pay'],
        ['InstaPay', 'Meeza', 'Fawry OTC', 'Visa', 'Mastercard']],
    'Saudi Arabia': [
        ['urpay', 'stc bank', 'Mobily Pay', 'Alinma Pay'],
        ['sarie', 'mada', 'Visa', 'Mastercard']],
    'Nigeria': [
        ['OPay', 'PalmPay', 'Paga'],
        ['NIBSS NIP', 'NQR', 'Verve', 'AfriGO', 'Visa', 'Mastercard']],
}


def _spans(page):
    return [s for b in page.get_text('dict')['blocks'] for l in b.get('lines', [])
            for s in l['spans'] if s['text'].strip()]


def _extract(page, country):
    spans = _spans(page)
    ordered = lambda items: sorted(items, key=lambda s: (round(s['origin'][1], 1), s['origin'][0]))
    intro = ' '.join(s['text'] for s in ordered([
        s for s in spans if 100 < s['origin'][1] < 153 and s['origin'][0] < 100]))
    headings = ordered([s for s in spans if s['text'].strip() in
                        ['Acceptance', 'Disbursements', 'Remittance']
                        and 300 < s['origin'][1] < 650])
    headings = [h for h in headings if any(
        s['text'] == 'Coverage' and 0 < s['origin'][1] - h['origin'][1] < 25
        for s in spans)]
    services = []
    row_names = {'Coverage', 'Checkout', 'Tokenisation', 'Refunds', 'Limits',
                 'Payout', 'Funding', 'OTC collection', 'Account validation'}
    for i, heading in enumerate(headings):
        start = heading['origin'][1]
        end = headings[i + 1]['origin'][1] if i + 1 < len(headings) else 790
        section = [s for s in spans if start - .8 <= s['origin'][1] < end - .8]
        labels = ordered([s for s in section if s['origin'][0] < 100 and s['text'] in row_names])
        rows = []
        for j, label in enumerate(labels):
            y = label['origin'][1]
            next_y = labels[j + 1]['origin'][1] if j + 1 < len(labels) else y + 12
            values = ordered([s for s in section if 145 < s['origin'][0] < 200
                              and y - 1 <= s['origin'][1] < next_y - 1])
            value = ' '.join(s['text'] for s in values)
            assert value, (country, heading['text'], label['text'])
            rows.append([label['text'], value])
        success_label = next(s for s in section if s['text'] == 'SUCCESS RATE')
        y = success_label['origin'][1]
        metrics = ordered([s for s in section if y + 2 < s['origin'][1] < y + 16])
        speed = next(s['text'] for s in metrics if s['origin'][0] < 100)
        success = next(s['text'] for s in metrics if 200 < s['origin'][0] < 300)
        uptime = next(s['text'] for s in metrics if 370 < s['origin'][0] < 410)
        services.append({'name': heading['text'], 'rows': rows,
                         'speed': speed, 'success': success, 'uptime': uptime})
    assert services and intro, country
    return {'country': country, 'intro': intro, 'services': services}


def apply(doc, H):
    for name, file in [('IR', 'Inter.ttf'), ('IB', 'InterSemi.ttf'), ('PH', 'Poppins.ttf')]:
        pdfmetrics.registerFont(TTFont(name, str(H / 'fonts' / file)))
    original = fitz.open(H / 'input' / 'Simpaisa_Network_Playbook_2026_V2_4.pdf')
    evidence = json.loads((H / 'regional-evidence-data.json').read_text())
    content = [_extract(doc[evidence[c]['page'] - 1], c) for c in METHODS]
    # Brand artwork remains an image; all body text, lines and charts are native.
    logo_svg = fitz.open(stream=(H.parent / 'assets' / 'simpaisa-0ddcd8e522.svg').read_bytes(), filetype='svg')
    logo_doc = fitz.open(stream=logo_svg.convert_to_pdf(), filetype='pdf')
    logo = logo_doc[0].get_pixmap(matrix=fitz.Matrix(4, 4), alpha=True).tobytes('png')
    stream = BytesIO()
    width, height = doc[8].rect.width, doc[8].rect.height
    c = Canvas(stream, pagesize=(width, height), pageCompression=1, invariant=1)
    navy, blue, body, gray = DEEP_NAVY, BRIGHT_BLUE, DEEP_GRAY, LIGHT_GRAY
    muted = (.32, .39, .50)
    panel = (.943, .957, 1)
    log = []

    def rect(x, y, w, h, fill, radius=0):
        c.setFillColorRGB(*fill)
        if radius:
            c.roundRect(x, height-y-h, w, h, radius, fill=1, stroke=0)
        else:
            c.rect(x, height-y-h, w, h, fill=1, stroke=0)

    def rule(x1, y1, x2, y2, color=gray, weight=.5):
        c.setStrokeColorRGB(*color); c.setLineWidth(weight)
        c.line(x1, height-y1, x2, height-y2)

    def text(t, x, baseline, size=8, font='IR', color=navy, align='left'):
        c.setFillColorRGB(*color); c.setFont(font, size)
        if align == 'center': c.drawCentredString(x, height-baseline, t)
        elif align == 'right': c.drawRightString(x, height-baseline, t)
        else: c.drawString(x, height-baseline, t)

    def wrap(t, max_width, size, font='IR'):
        lines=[]; current=''
        for word in t.split():
            candidate=(current+' '+word).strip()
            if pdfmetrics.stringWidth(candidate, font, size)>max_width and current:
                lines.append(current); current=word
            else: current=candidate
        if current: lines.append(current)
        return lines

    for item in content:
        country = item['country']; entry = evidence[country]; page_index = entry['page']-1
        p = original[page_index]
        header = next(im for im in p.get_images(full=True) if im[2] == 2380 and im[3] == 624)
        c.drawImage(ImageReader(BytesIO(original.extract_image(header[0])['image'])), 0, height-156, width=595, height=156)
        c.drawImage(ImageReader(BytesIO(logo)), 40, height-39.5, width=84, height=23.5, mask='auto')
        flag = p.get_pixmap(matrix=fitz.Matrix(5,5), clip=fitz.Rect(518,18,548,39), alpha=False).tobytes('png')
        c.drawImage(ImageReader(BytesIO(flag)), 518, height-39, width=30, height=21)
        text(country, 40, 69, 24, 'PH', WHITE)
        subtitle = ' · '.join(s['name'] for s in item['services'])
        text(subtitle, 40, 89, 8.2, color=WHITE)
        intro = wrap(item['intro'], 515, 8.4)
        assert len(intro)<=3, country
        for i, line in enumerate(intro): text(line, 40, 113+i*11.2, 8.4, color=WHITE)

        rect(40,163,515,125,panel,5)
        text('Market evidence',52,184,10,'IB')
        for j,a in enumerate(entry['panels']):
            x=52+j*166
            if j: rule(x-8,190,x-8,265,(.79,.84,.93),.5)
            text(a['title'],x,199,8.3,'IB')
            text(a['unit'],x,211,6.5,color=muted)
            if a.get('kind') == 'pie':
                colors=[blue,(.32,.52,.88),(.53,.66,.90),(.69,.77,.92),(.83,.87,.95)]
                cx=x+26; cy=height-242; angle=90; total=sum(a['values'])
                for k,(name,value) in enumerate(zip(a['names'],a['values'])):
                    frac=value/total
                    c.setFillColorRGB(*colors[k]); c.setStrokeColorRGB(*WHITE); c.setLineWidth(.5)
                    c.wedge(cx-23,cy-23,cx+23,cy+23,angle,-frac*360,fill=1,stroke=1)
                    angle-=frac*360; yy=224+k*10
                    rect(x+57,yy-5,4,4,colors[k])
                    text(name,x+65,yy,6.5,color=muted)
                    text(f'{frac*100:.1f}%',x+151,yy,6.5,'IB',align='right')
            else:
                percent=a['unit'].startswith('%'); domain=100 if percent else max(a['values'])*1.12
                for k,(label,value) in enumerate(zip(a['labels'],a['values'])):
                    y=223+k*24; bar_width=64*value/domain
                    text(label,x,y+5,6.9,color=muted)
                    rect(x+44,y,bar_width,9,blue if k else (.71,.79,.94))
                    digits=2 if 'trillion' in a['unit'] or 'billion' in a['unit'] else 1
                    value_text=f'{value:,.{digits}f}'+('%' if percent else '')
                    if country=='Iraq' and j==0 and k==1: value_text='~'+value_text
                    text(value_text,x+48+bar_width,y+6,7.1,'IB')
                rule(x+44,260,x+108,260,(.79,.84,.93))
            c.linkURL(a['source'],(x,height-272,x+151,height-188),relative=0,thickness=0)
        text(entry['note'],52,280,7,color=muted)

        text('Simpaisa services',40,312,10,'IB')
        top=325
        for i,service in enumerate(item['services']):
            rows=[(label,wrap(value,389,8)) for label,value in service['rows']]
            row_heights=[max(12,len(lines)*10.2) for _,lines in rows]
            h=50+sum(row_heights)
            rect(40,top,515,h,panel if i%2==0 else WHITE)
            text(service['name'],50,top+12,9,'IB')
            code={'Acceptance':'C2B','Disbursements':'B2C','Remittance':'C2C'}[service['name']]
            text(code,141,top+12,6.8,'IB',blue)
            yy=top+25
            for (label,lines),row_h in zip(rows,row_heights):
                text(label,50,yy,8,'IB')
                for li,line in enumerate(lines):text(line,154,yy+li*10.2,8,color=body)
                yy+=row_h
            rule(50,yy-4,545,yy-4,(.79,.84,.93),.5)
            labels=['CONFIRMATION' if service['name']=='Acceptance' else 'SPEED','SUCCESS RATE','RELIABILITY']
            for x,label,value in zip([50,217,386],labels,[service['speed'],service['success'],service['uptime']]):
                text(label,x,yy+4,5.5,color=muted)
                text(value,x,yy+15,7.2,'IB')
            top+=h+6

        # A full-width, uncropped band starts at a consistent gap after services.
        bar_top=top; rect(40,bar_top,515,20,navy)
        bar_label='Full service coverage' if len(item['services'])==3 else subtitle
        text(bar_label,50,bar_top+13,8.2,color=WHITE)
        text('Single API integration',545,bar_top+13,8.2,'IB',WHITE,'right')
        heading_y=bar_top+38
        text('Key payment methods',40,heading_y,10,'IB')
        lanes_top=heading_y+10
        # Category labels have their own fixed column. Method cells start at the
        # same x on both rows and in every market; long names wrap within cells.
        method_x=157; method_width=398; lane_h=30
        for lane_index,names in enumerate(METHODS[country]):
            y=lanes_top+lane_index*lane_h; middle=y+15
            categories=['DOMESTIC WALLETS'] if lane_index==0 else ['LOCAL RAILS', 'AND CARDS']
            for k,label in enumerate(categories):
                text(label,40,middle+2.4+(k-(len(categories)-1)/2)*9,6.7,'IB',blue)
            cell_width=method_width/len(names)
            for j,name in enumerate(names):
                x=method_x+j*cell_width
                if j: rule(x,y+7,x,y+23,gray,.45)
                lines=wrap(name,cell_width-6,7.6,'IB')
                assert len(lines)<=2,(country,name)
                for k,line in enumerate(lines):
                    text(line,x+cell_width/2,middle+2.7+(k-(len(lines)-1)/2)*9.1,7.6,'IB',navy,'center')
            rule(40,y+lane_h,555,y+lane_h,gray,.55)
        bottom=lanes_top+2*lane_h
        assert bottom<786,(country,bottom)
        rule(40,794,555,794,gray,.6)
        text('www.simpaisa.com',40,811,7.5,color=(.4,.4,.4))
        c.linkURL('https://www.simpaisa.com/',(40,height-814,115,height-802),relative=0,thickness=0)
        text(f'{page_index+1:02}',555,811,7.5,color=(.4,.4,.4),align='right')
        log.append({'country':country,'page':page_index+1,'service_bar_top':bar_top,
                    'heading_baseline':heading_y,'lanes_top':lanes_top,'lanes_bottom':bottom,
                    'category_x':40,'methods_x':method_x,'lane_height':lane_h,
                    'methods':sum(METHODS[country],[])})
        c.showPage()
    c.save()
    replacement=fitz.open(stream=stream.getvalue(),filetype='pdf')
    for page_index in range(14,7,-1):doc.delete_page(page_index)
    doc.insert_pdf(replacement,start_at=8)
    (H/'build'/'regional-option3-layout.json').write_text(json.dumps(log,indent=2)+'\n')
    (H/'build'/'regional-preserved-content.json').write_text(json.dumps(content,indent=2)+'\n')
