"""Complete Egypt and Saudi payout tables and add Fawry collection coverage."""
from pathlib import Path
import sys,json,fitz
HERE=Path(__file__).resolve().parent
SRC=Path(sys.argv[1]) if len(sys.argv)>1 else HERE/'build/Simpaisa_Network_Playbook_2026_Network_Update.pdf'
OUT=Path(sys.argv[2]) if len(sys.argv)>2 else HERE/'build/Simpaisa_Network_Playbook_2026_Complete.pdf'
d=fitz.open(SRC)
F={k:fitz.Font(fontfile=str(HERE/'fonts'/v)) for k,v in [('IR','Inter.ttf'),('IB','InterSemi.ttf'),('PH','Poppins.ttf')]}
NAVY=(0,.094,.4);BLUE=(.004,.337,.984);BODY=(.20,.27,.39);WHITE=(1,1,1);MUTED=(.32,.39,.50);PALE=(.943,.957,1);LINE=(.79,.84,.93)
log=[]
def wrap(t,size,w,font='IR'):
 lines=[];line=''
 for word in t.split():
  s=(line+' '+word).strip()
  if F[font].text_length(s,fontsize=size)<=w:line=s
  else:lines.append(line);line=word
 lines.append(line);return lines

def text(p,r,t,size=8.4,font='IR',color=BODY,leading=None):
 r=fitz.Rect(r);leading=leading or size*1.25;lines=wrap(t,size,r.width,font)
 assert len(lines)*leading<=r.height+.5,('overflow',p.number+1,t,r,lines)
 for j,line in enumerate(lines):p.insert_text((r.x0,r.y0+F[font].ascender*size+j*leading),line,fontname=font,fontsize=size,color=color)
 log.append({'page':p.number+1,'text':t,'rect':list(r)})
def fonts(p):
 for k,v in [('IR','Inter.ttf'),('IB','InterSemi.ttf'),('PH','Poppins.ttf')]:p.insert_font(fontname=k,fontfile=str(HERE/'fonts'/v))

egypt=[
('Acceptance','C2B',[
('Coverage','Wallets, bank transfers, cards and OTC collection'),
('Checkout','Wallets: phone number, PIN and OTP in app; InstaPay: IPN PIN or biometric; hosted card page'),
('OTC collection','OTC payment network spans over 300,000 POS terminals across Egypt'),
('Refunds','Available'),
('Limits','InstaPay: EGP 70,000/transfer; wallet limits depend on the provider.')],('CONFIRMATION','Real-time','Above 80%')),
('Disbursements','B2C',[
('Coverage','Wallets and bank accounts'),('Payout','Direct to wallet or bank account'),
('Limits','Receiving account and wallet balance limits apply by provider.')],('SPEED','Real-time payout','Above 96%')),
('Remittance','C2C',[
('Coverage','Wallets and bank accounts'),('Funding','USD prefund'),('Payout','Direct to wallet or bank account'),
('Limits','Receiving account and wallet balance limits apply by provider.')],('SPEED','Real-time payout','Above 98.5%'))]
saudi=[
('Acceptance','C2B',[
('Coverage','Wallets, bank transfers and cards'),
('Checkout','mada hosted page with 3-D Secure; sarie transfer in the banking app; wallets: OTP or in-app'),
('Refunds','Available'),('Limits','sarie: up to SAR 20,000/transfer; other bank and wallet limits depend on provider.')],('CONFIRMATION','Real-time','Above 80%')),
('Disbursements','B2C',[
('Coverage','Wallets and bank accounts'),('Payout','Direct to supported wallet or bank account'),
('Account validation','Bank beneficiary verification; wallet validation depends on provider.'),
('Limits','sarie: up to SAR 20,000/transfer; other bank and wallet limits depend on provider.')],('SPEED','Real-time payout','Above 96%'))]

for n,start,services in [(13,325,egypt),(14,380,saudi)]:
 p=d[n-1]
 for l in p.get_links():
  if fitz.Rect(l['from']).intersects(fitz.Rect(39,start-3,556,697)):p.delete_link(l)
 p.add_redact_annot((39,start-3,556,697),fill=WHITE,cross_out=False);p.apply_redactions(images=0,graphics=2,text=0);fonts(p)
 y=start
 for k,(name,tag,rows,metrics) in enumerate(services):
  heights=[max(12,len(wrap(v,8.4,391))*10.5) for _,v in rows]
  height=23+sum(heights)+27
  if k%2==0:p.draw_rect((40,y,555,y+height),fill=PALE,color=None)
  text(p,(50,y+4,139,y+20),name,9.2,'PH',NAVY)
  text(p,(141,y+6,175,y+18),tag,7.4,'IB',BLUE)
  yy=y+23
  for (label,value),h in zip(rows,heights):
   text(p,(50,yy,149,yy+h),label,8.4,'IB',NAVY)
   text(p,(154,yy,545,yy+h),value,8.4)
   if label=='OTC collection':p.insert_link({'kind':fitz.LINK_URI,'from':fitz.Rect(154,yy,545,yy+h),'uri':'https://www.fawry.com/consumer/bill-payment/'})
   if label=='Limits':p.insert_link({'kind':fitz.LINK_URI,'from':fitz.Rect(50,yy,545,yy+h),'uri':'https://www.cbe.org.eg/en/payment-systems-and-services/instant-payment-network' if n==13 else 'https://www.sama.gov.sa/en-US/payment/pages/sarie.aspx'})
   yy+=h
  p.draw_line((50,yy),(545,yy),color=LINE,width=.7)
  for x,label,value in [(50,metrics[0],metrics[1]),(217.7,'SUCCESS RATE',metrics[2]),(385.3,'RELIABILITY','Multi-rail, above 99.9% uptime')]:
   text(p,(x,yy+3,x+160,yy+13),label,6.8,'IB',MUTED)
   text(p,(x,yy+12,x+160,yy+26),value,8.4,'IB',NAVY)
  y+=height
 assert y+31<701,(n,y)
 p.draw_rect((40,y+6,555,y+31),fill=NAVY,color=None)
 text(p,(50,y+12,350,y+26),'All three flows' if n==13 else 'Acceptance · Disbursements',9,color=WHITE)
 text(p,(433,y+12,550,y+26),'Single API integration',9,color=WHITE)
# Preserve the six first-row Egypt logos; rebalance the second row and add Fawry.
p=d[12];bottom=[i for i in p.get_image_info(xrefs=True) if 758<i['bbox'][1]<791];assert len(bottom)==2
assets=[]
for i in sorted(bottom,key=lambda v:v['bbox'][0]):
 meta=d.extract_image(i['xref']);pix=fitz.Pixmap(d,i['xref'])
 if meta.get('smask'):pix=fitz.Pixmap(pix,fitz.Pixmap(d,meta['smask']))
 assets.append(pix.tobytes('png'))
p.add_redact_annot((40,758,555,792),fill=WHITE,cross_out=False);p.apply_redactions(images=1,graphics=2,text=0)
p.insert_image((170,764,237,786),stream=assets[0],keep_proportion=True)
p.insert_image((280,764,315,786),stream=assets[1],keep_proportion=True)
p.insert_image((355,764,429,787),filename=str(HERE.parent/'assets/fawry-16b2a0cb0c.png'),keep_proportion=True)
# Reflect the added collection method in the existing acceptance and setup summaries.
changes=[(16,(125,345,225,391),'Vodafone Cash, e& Cash, Orange Cash and WE Pay; InstaPay; Meeza and international cards; Fawry',7.8,9),
(16,(237,345,351,391),'Wallet: PIN and OTP. InstaPay: PIN or biometric. Hosted card checkout. Fawry: reference code.',8.0,10),
(18,(125,425,329,453),'Enable wallets, InstaPay, cards and Fawry collections. Test method authentication.',8.5,10.5),
(18,(344,425,548,454),'Disbursements and remittance: wallets and bank accounts.',8.5,10.5),
(18,(344,457,548,486),'Disbursements to wallets and bank accounts. No remittance payout.',8.5,10.5)]
for n,r,t,size,leading in changes:
 p=d[n-1];p.add_redact_annot(r,fill=False,cross_out=False);p.apply_redactions(images=0,graphics=0,text=0);fonts(p);text(p,r,t,size,leading=leading)
# Primary-source corrections: telecom wallets are a matched-quarter series.
p=d[12]
for r in [(49,188,206,275),(217,188,375,275),(386,188,545,275)]:p.add_redact_annot(r,fill=PALE,cross_out=False)
p.apply_redactions(images=0,graphics=1,text=0);fonts(p)
for x,title,unit,values,labels,maximum,growth in [(50,'Telecom-wallet value','EGP bn | Q2 2025 ≈ USD 18.9bn',[547.6,943.4],['547.6','943.4'],1000,'+72%'),(218.6,'Telecom-wallet adoption','Active wallets, millions',[35.8,46.3],['35.8','46.3'],60,'+29%')]:
 text(p,(x,190,x+156,202),title,8.8,'IB',NAVY)
 text(p,(x,204,x+156,216),unit,6.9,color=MUTED)
 text(p,(x+128,218,x+156,231),growth,8.7,'IB',BLUE)
 for j,(v,label) in enumerate(zip(values,labels)):
  yy=232+j*18
  text(p,(x,yy,x+33,yy+11),'Q2 2024' if j==0 else 'Q2 2025',6.8,color=MUTED)
  start=x+37;w=87*v/maximum
  p.draw_rect((start,yy,start+w,yy+7),fill=(.70,.79,.97) if j==0 else BLUE,color=None)
  text(p,(start+w+3,yy-1,x+156,yy+11),label,7.5,'IB',NAVY)
 for v in [0,maximum/2,maximum]:
  xx=x+37+87*v/maximum
  text(p,(xx-5,265,xx+22,274),str(int(v)),6.5,color=MUTED)
text(p,(387.3,190,545,202),'Access, InstaPay and Meeza',8.8,'IB',NAVY)
for y,l,v,note in [(207,'Account use','79%','56.4m / 71.4m adults'),(233,'IPN / InstaPay','Nationwide','24/7 instant transfers'),(256,'Meeza','Domestic','EGP card payments')]:
 text(p,(387.3,y,452,y+11),l,7.4,color=MUTED)
 text(p,(453.3,y-2,545,y+10),v,8.6,'IB',NAVY)
 text(p,(453.3,y+10,545,y+20),note,6.5,color=MUTED)
text(p,(387.3,217,451,228),'Jun 2026 | age 15+',6.5,color=MUTED)
# Replace the unsupported annual wallet-value sentence in the country introduction.
p.add_redact_annot((40,105,555,144),fill=False,cross_out=False);p.apply_redactions(images=0,graphics=0,text=0);fonts(p)
text(p,(40,106,555,145),'Egypt had 46.3m active telecom-operator wallets in Q2 2025. Their quarterly transaction value reached EGP 943.4bn (about USD 18.9bn), up 72% year on year. Simpaisa supports collections, disbursements and remittance payout through local payment methods.',9,color=WHITE,leading=11.8)
for r,url in [((49,188,375,276),'https://www.tra.gov.eg/en/ntra-issues-q2-2025-report-on-the-usage-indicators-of-mobile-wallets-operated-by-telecom-companies/'),((386,204,545,230),'https://www.cbe.org.eg/en/news-publications/news/2026/08/06/09/00/financial-inclusion-rates-6-aug-26'),((386,232,545,276),'https://www.cbe.org.eg/en/payment-systems-and-services/instant-payment-network')]:p.insert_link({'kind':fitz.LINK_URI,'from':fitz.Rect(r),'uri':url})
# Keep the national market table aligned and synchronize the verified Egypt figures.
data=json.loads((HERE/'network-market-data.json').read_text())
p=d[7]
for i,row in enumerate(data['rows']):
 for j,value in enumerate(row):
  x=113+j*98;y=166+i*46
  p.add_redact_annot((x+.3,y+.3,x+97.7,y+45.7),fill=(.925,.949,.984),cross_out=False)
p.apply_redactions(images=0,graphics=0,text=0);fonts(p)
for i,row in enumerate(data['rows']):
 for j,value in enumerate(row):
  x=113+j*98;y=166+i*46
  # Keep the primary figure and its definition on separate lines.
  yy=y+5
  for k,para in enumerate(value.split('\n')):
   font='IB' if k==0 else 'IR'
   lines=wrap(para,7.8,84,font)
   text(p,(x+8,yy,x+92,y+45),para,7.8,font,color=NAVY,leading=10.1)
   yy+=len(lines)*10.1
  p.draw_rect((x,y,x+98,y+46),color=(.82,.86,.94),width=.35)
# Repeat only source-backed market measures in the opportunity table.
p=d[6]
updates=[((144,595,269,608),'46.3m active wallets',8.2,'IB'),((144,608,269,621),'Telecom-operator wallets',7.6,'IR'),((144,620,269,632),'NTRA | Q2 2025',7.1,'IR'),((284.33,595,412,608),'IPN / InstaPay',8.2,'IB'),((284.33,608,412,621),'Nationwide instant transfers',7.6,'IR'),((284.33,620,412,632),'CBE | network coverage',7.1,'IR'),((424.66,595,548,608),'Meeza',8.2,'IB'),((424.66,608,548,621),'Domestic card scheme',7.6,'IR'),((424.66,620,548,632),'CBE | network coverage',7.1,'IR')]
for r,t,size,font in updates:p.add_redact_annot(r,fill=False,cross_out=False)
p.apply_redactions(images=0,graphics=0,text=0);fonts(p)
for r,t,size,font in updates:text(p,r,t,size,font,NAVY if font=='IB' else MUTED)
# Distinguish domestic schemes from issuer/acquirer networks in both market tables.
fixes=[(7,(40,367,555,383),'Wallets, A2A and local card networks by market',11,'PH',NAVY),(7,(284.33,463,414,476),'93.9m NPSB IBFT',8.2,'IB',NAVY),(7,(284.33,683,414,696),'~11bn NIP payments',8.2,'IB',NAVY),(8,(317,149,404,164),'DOMESTIC CARD SCHEME',6.2,'IB',WHITE),(8,(40,494,555,519),"Market figures are reported by central banks, regulators and official industry sources, not Simpaisa volumes. Coverage shows Simpaisa services.",7.4,'IR',MUTED),(8,(54,589,284,602),'Domestic card scheme',9,'IB',BLUE),(8,(54,603,284,628),'Domestic card schemes are shown separately from international card networks.',8.3,'IR',BODY),(7,(424.66,551,548,563),'No live domestic',8.2,'IB',NAVY),(7,(424.66,563,548,575),'card scheme',7.6,'IR',MUTED),(7,(424.66,576,548,587),'',7.1,'IR',MUTED),(7,(424.66,419,548,432),'PayPak',8.2,'IB',NAVY),(7,(424.66,432,548,444),'Domestic card scheme',7.6,'IR',MUTED),(7,(424.66,444,548,455),'1LINK | scheme',7.1,'IR',MUTED)]
# Keep repeated current-market entries aligned with the refreshed overview.
fixes += [(7,(144,419,269,432),'150.8m accounts',8.2,'IB',NAVY),(7,(144,444,269,455),'SBP | Dec 2025',7.1,'IR',MUTED),(7,(144,463,269,476),'257.0m MFS accounts',8.2,'IB',NAVY),(7,(144,488,269,499),'BB | Jun 2026',7.1,'IR',MUTED),(7,(144,507,269,520),'27.7m wallet users',8.2,'IB',NAVY),(7,(144,532,269,543),'NRB | Jul 2026',7.1,'IR',MUTED),(7,(284.33,507,414,520),'1.60m connectIPS users',8.2,'IB',NAVY),(7,(284.33,532,414,543),'NRB | Jul 2026',7.1,'IR',MUTED)]
for n,r,t,size,font,color in fixes:
 p=d[n-1];p.add_redact_annot(r,fill=False,cross_out=False)
for n in [7,8]:d[n-1].apply_redactions(images=0,graphics=0,text=0);fonts(d[n-1])
for n,r,t,size,font,color in fixes:text(d[n-1],r,t,size,font,color)
p=d[7]
for l in p.get_links():
 if fitz.Rect(l['from']).intersects(fitz.Rect(113,166,505,488)):p.delete_link(l)
for key,url in data['cell_sources'].items():
 i,j=map(int,key.split(','));x=113+j*98;y=166+i*46
 p.insert_link({'kind':fitz.LINK_URI,'from':fitz.Rect(x,y,x+98,y+46),'uri':url})
OUT.parent.mkdir(parents=True,exist_ok=True);d.save(OUT,garbage=4,deflate=True)
(OUT.parent/'payout-completion-log.json').write_text(json.dumps(log,indent=2));print(OUT)
