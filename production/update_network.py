"""Apply approved network-positioning and coverage edits to the prior PDF build."""
from pathlib import Path
import sys,fitz,json,re
HERE=Path(__file__).resolve().parent
SOURCE=Path(sys.argv[1]) if len(sys.argv)>1 else HERE/'build/Simpaisa_Network_Playbook_2026_Final.pdf'
DEST=Path(sys.argv[2]) if len(sys.argv)>2 else HERE/'build/Simpaisa_Network_Playbook_2026_Network_Update.pdf'
doc=fitz.open(SOURCE);original=fitz.open(SOURCE)
F={k:fitz.Font(fontfile=str(HERE/'fonts'/v)) for k,v in [('IR','Inter.ttf'),('IB','InterSemi.ttf'),('PH','Poppins.ttf')]}
NAVY=(0,.094,.4);BLUE=(.004,.337,.984);BODY=(.20,.27,.39);WHITE=(1,1,1);MUTED=(.32,.39,.50);GREY=(.914,.914,.914);PALE=(.925,.949,.984)
ops=[];logs=[]
def add(n,rect,t,size=9.6,font='IR',color=BODY,clear=None,fill=None,leading=None):ops.append(dict(n=n,rect=rect,t=t,size=size,font=font,color=color,clear=clear or rect,fill=fill,leading=leading or size*1.28))
def findblock(n,needle,t,**kw):
 bs=[b for b in original[n-1].get_text('blocks') if needle in ' '.join(b[4].split())];assert len(bs)==1,(n,needle,bs)
 b=bs[0];add(n,(b[0],b[1],555,b[3]+2),t,clear=b[:4],**kw)
def drawtext(page,o):
 r=fitz.Rect(o['rect']);font=F[o['font']];size=o['size'];lines=[]
 for para in o['t'].split('\n'):
  line=''
  for w in para.split():
   test=(line+' '+w).strip()
   if font.text_length(test,fontsize=size)<=r.width:line=test
   else:lines.append(line);line=w
  lines.append(line)
 height=size*(font.ascender-font.descender)+(len(lines)-1)*o['leading'];assert height<=r.height+.4,(page.number+1,o['t'],height,r)
 for j,line in enumerate(lines):page.insert_text((r.x0,r.y0+font.ascender*size+j*o['leading']),line,fontname=o['font'],fontsize=size,color=o['color'])
 logs.append(dict(page=page.number+1,text=o['t'],rect=list(r)))
# Cover subtitle: native PDF text over a narrow background repair, preserving the artwork.
add(1,(40,369,555,414),'Local Payment Networks Across Emerging Markets',16,'IR',(.77,.84,1),clear=(38,366,330,413))
intro='Simpaisa builds and operates a country-level network of wallets, banks, switches, domestic schemes and licensed partners. We choose the right access architecture by market, manage routing and redundancy across those rails, govern settlement and reconciliation, and continuously optimise the network for coverage, cost and quality.'
add(2,(40,76,555,137),intro,9.5,clear=(40,74,555,112),leading=12.2)
# Move the flag row within the existing space beneath the expanded introduction.
# Original flag row fits beneath the expanded introduction.
add(4,(40,142,555,207),'Our network supports merchant acceptance (C2B), disbursements (B2C) and remittance (C2C). We design and manage the local network for you, and you access that entire network through one API. Licensed partners handle funds; Simpaisa provides payment processing, routing and reconciliation.',10,clear=(40,140,555,202),leading=14)
add(4,(313.5,288,542.5,373),'Send disbursements and remittance payouts to supported wallets and bank accounts. Settlement and payout structures are implemented through licensed banking and payment partners according to the regulatory and network model in each market. Destination, timing and settlement terms depend on the market and method.',9.3,color=WHITE,clear=(312,286,544,370),leading=11.8)
add(6,(40,140,555,178),'Funds are held and moved through the relevant licensed banking or payment partner. Simpaisa provides the processing, routing, reconciliation and settlement instructions required by the operating model.',9.6,clear=(40,138,555,180),leading=13)
add(6,(200,642,544,666),'Services are provided within the applicable regulatory framework through Simpaisa entities and/or appropriately licensed partners',8.3,color=WHITE,clear=(199,641,544,668),leading=10.5)
add(6,(200,721,544,735),'Real-time transaction visibility and reporting',8.3,color=WHITE,clear=(199,720,544,735))
add(7,(53,201.3,238,212),'Registered accounts, not unique individuals',8,color=MUTED,clear=(53,200,239,212))
# Preserve the account unit after the requested chart subtitle replacement.
for block in original[6].get_text('dict')['blocks']:
 for line in block.get('lines',[]):
  for span in line['spans']:
   if span['text'] in ['106.9','120.2','135.9'] and span['bbox'][0]<295 and 210<span['bbox'][1]<330:
    r=fitz.Rect(span['bbox']);add(7,(r.x0,r.y0,r.x1+14,r.y1+1),span['text']+'m',span['size'],'IB',NAVY,clear=r)
add(7,(52,752,543,779),'International businesses cannot efficiently integrate, govern, settle and operate dozens of fragmented local payment systems country by country.',9.2,color=WHITE,clear=(52,752,543,780),leading=12.5)
# Coverage summaries: six disbursement markets; five have all three services.
for n in [2,8,18]:
 for b in original[n-1].get_text('blocks'):
  txt=' '.join(b[4].split())
  if 'disbursements in four' in txt:add(n,(b[0],b[1],b[2]+5,b[3]+4),txt.replace('disbursements in four','disbursements in six'),9.6,color=WHITE if n==8 else BODY,clear=b[:4],leading=13)
for n in [3,18]:
 for r in original[n-1].search_for('Going live across the network'):
  add(n,(r.x0,r.y0,555,r.y1+3),'Connecting a merchant to the network',20 if n==18 else 10,'PH' if n==18 else 'IB',NAVY,clear=r)
findblock(3,'Wallets, InstaPay and Meeza; acceptance and remittance.','Wallets, InstaPay and Meeza; all three flows.',size=7.5,color=MUTED)
findblock(3,'mada, sarie and wallets; acceptance.','mada, sarie and wallets; acceptance and disbursements.',size=7.5,color=MUTED)
# Existing country services stay unchanged; new disbursement availability carries no invented metrics.
add(13,(40,80,555,94),'Acceptance · Disbursements · Remittance',8.2,color=WHITE,clear=(40,79,300,94))
add(14,(40,80,555,94),'Acceptance · Disbursements',8.2,color=WHITE,clear=(40,79,300,94))
add(13,(40,449,555,626),'',fill=WHITE)
add(13,(50,452,139,468),'Disbursements',9.2,'PH',NAVY)
add(13,(141,454,170,467),'B2C',7.4,'IB',BLUE)
add(13,(50,476,149,489),'Coverage',8.6,'IB',NAVY)
add(13,(154,476,545,489),'Available',8.6,color=BODY)
add(14,(39,504,556,540),'',fill=WHITE)
add(14,(50,513,139,529),'Disbursements',9.2,'PH',NAVY)
add(14,(141,515,170,528),'B2C',7.4,'IB',BLUE)
add(14,(50,537,149,550),'Coverage',8.6,'IB',NAVY)
add(14,(154,537,545,550),'Available',8.6,color=BODY)
add(18,(344,425,548,452),'Disbursements available. Remittance payout to wallets and bank accounts.',8.5,clear=(344,424,548,454),leading=10.5)
add(18,(344,457,548,484),'Disbursements available. No remittance payout. Agree settlement with the licensed partner.',8.5,clear=(344,456,548,486),leading=10.5)
# Table entries supplied separately after primary-source review.
data=json.loads((HERE/'network-market-data.json').read_text())
add(8,(40,121,345,135),'Market context and service coverage',8.3,color=MUTED,fill=GREY)
add(8,(507,149,554,163),'COVERAGE',6.4,'IB',WHITE,clear=(505,149,554,162))
for i,row in enumerate(data['rows']):
 y=166+i*46
 for j,t in enumerate(row):
  x=113+j*98;add(8,(x+8,y+5,x+92,y+45),t,7.8,color=NAVY,clear=(x+.3,y+.3,x+97.7,y+45.7),fill=PALE,leading=10.1)
add(8,(40,494,555,515),'Market statistics describe national accounts, users or payment activity. They are not Simpaisa operating figures. Coverage indicates Simpaisa services; payout rails describe the market infrastructure.',7.8,color=MUTED,clear=(40,493,555,516),leading=10.2)
add(8,(54,563,284,586),'National wallet or e-money accounts. Provider customer counts are excluded.',8.3,clear=(53,562,285,587),leading=10.5)
add(8,(306.5,589,547,602),'Payout rails and coverage',9,'IB',BLUE,clear=(306,588,548,602))
add(8,(306.5,603,546,629),'Market infrastructure, separate from Simpaisa coverage. A: acceptance. D: disbursements. R: remittance.',8.3,clear=(306,602,548,630),leading=10.5)
add(8,(292.5,724.2,315,747),'5',15,'PH',WHITE,clear=(289,724,308,747))
for n in range(1,20):
 page=doc[n-1];these=[o for o in ops if o['n']==n]
 for o in these:page.add_redact_annot(fitz.Rect(o['clear']),fill=False,cross_out=False)
 if these:page.apply_redactions(images=0,graphics=0,text=0)
 for k,v in ([('IR','Inter.ttf'),('IB','InterSemi.ttf'),('PH','Poppins.ttf')] if these else []):page.insert_font(fontname=k,fontfile=str(HERE/'fonts'/v))
 for o in these:
  if o['fill'] is not None:page.draw_rect(fitz.Rect(o['clear']),fill=o['fill'],color=None)
  if n==1:
   # Opaque gradient repair removes old lettering embedded in cover artwork.
   from PIL import Image
   import io
   pix=original[0].get_pixmap(matrix=fitz.Matrix(2,2))
   patch=Image.new('RGB',(1034,96))
   for iy in range(96):
    col=pix.pixel(1120,732+iy)[:3]
    for ix in range(1034):patch.putpixel((ix,iy),col)
   buf=io.BytesIO();patch.save(buf,format='PNG')
   page.insert_image(fitz.Rect(38,366,555,414),stream=buf.getvalue(),overlay=True)
  if o['t']:drawtext(page,o)
# Flag row scaled as a group; all seven countries retained.

# Existing remittance block and API strip move as complete vector groups.
remittance=fitz.open()
remittance.insert_pdf(original,from_page=12,to_page=12)
rp=remittance[0]
for r in [(0,0,595,449),(0,590,595,842),(0,449,40,590),(555,449,595,590)]:
 rp.add_redact_annot(fitz.Rect(r),fill=False,cross_out=False)
rp.apply_redactions(images=1,graphics=2,text=0)
rp.set_cropbox(fitz.Rect(40,449,555,590))
assert 'Egypt' not in rp.get_text() and 'Acceptance' not in rp.get_text()
doc[12].show_pdf_page(fitz.Rect(40,494,555,635),remittance,0,keep_proportion=False)
for n,y,label in [(13,647,'All three flows'),(14,570,'Acceptance · Disbursements')]:
 page=doc[n-1];page.draw_rect((40,y,555,y+25),fill=NAVY,color=None)
 drawtext(page,dict(rect=(50,y+6,350,y+21),t=label,font='IR',size=9,color=WHITE,leading=11.5))
 drawtext(page,dict(rect=(433,y+6,550,y+21),t='Single API integration',font='IR',size=9,color=WHITE,leading=11.5))
# New disbursement ticks in the company footprint matrix.
for y in [541,561]:doc[3].draw_polyline([(386,y),(389,y+3),(394,y-3)],color=BLUE,width=.9)
# Activate D in the country coverage table, retaining its native badge style.
for y in [373,419]:
 page=doc[7];page.draw_rect((524,y-6,536,y+6),fill=BLUE,color=None,radius=.2)
 drawtext(page,dict(rect=(527.5,y-5.5,535.5,y+6),t='D',font='IB',size=7,color=WHITE,leading=9))
# Reporting links are bound to each national market row.
for i,url in enumerate(data['sources']):doc[7].insert_link({'kind':fitz.LINK_URI,'from':fitz.Rect(113,166+i*46,505,212+i*46),'uri':url})
toc=doc.get_toc()
for row in toc:
 if row[2]==18:row[1]='Connecting a merchant to the network'
doc.set_toc(toc)
DEST.parent.mkdir(parents=True,exist_ok=True);doc.save(DEST,garbage=4,deflate=True)
(DEST.parent/'network-update-log.json').write_text(json.dumps(logs,indent=2));print(DEST)
