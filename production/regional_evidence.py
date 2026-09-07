"""Uniform regional evidence and the requested recognition-tile removal."""
import fitz,json,math
from io import BytesIO
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.colors import HexColor

def apply(doc,H):
 F={k:fitz.Font(fontfile=str(H/'fonts'/v)) for k,v in [('IR','Inter.ttf'),('IB','InterSemi.ttf'),('PH','Poppins.ttf')]}
 N=(0,.094,.4);B=(.004,.337,.984);M=(.32,.39,.50);P=(.943,.957,1);W=(1,1,1);L=(.79,.84,.93)
 def fonts(p):
  for k,v in [('IR','Inter.ttf'),('IB','InterSemi.ttf'),('PH','Poppins.ttf')]:p.insert_font(fontname=k,fontfile=str(H/'fonts'/v))
 def text(p,t,x,y,w,size=8,font='IR',col=N,maxlines=2,align=False):
  lines=[];line=''
  for word in t.split():
   q=(line+' '+word).strip()
   if F[font].text_length(q,fontsize=size)>w:lines.append(line);line=word
   else:line=q
  lines.append(line);assert len(lines)<=maxlines,(t,lines)
  for i,l in enumerate(lines):
   xx=x+(w-F[font].text_length(l,fontsize=size))/2 if align else x
   p.insert_text((xx,y+F[font].ascender*size+i*size*1.22),l,fontname=font,fontsize=size,color=col)
 def box(p,r,col):p.draw_rect(r,color=None,fill=col)
 def clear(p,r,col):
  for link in p.get_links():
   if fitz.Rect(link['from']).intersects(r):p.delete_link(link)
  p.add_redact_annot(r,fill=col,cross_out=False);p.apply_redactions(images=0,graphics=0,text=0);fonts(p)
 data=json.loads((H/'regional-evidence-data.json').read_text())
 # Snapshot preserves all service-table text and vector artwork during reflow.
 snapshot=fitz.open(stream=doc.tobytes(),filetype='pdf')
 for country,item in data.items():
  p=doc[item['page']-1];old=snapshot[item['page']-1]
  service=old.search_for('Simpaisa services')[0]
  start=math.floor(service.y0)-3
  clear(p,fitz.Rect(39,162,556,707),W)
  # Twelve-point inner padding and the same panel/section spacing in every market.
  p.draw_rect((40,163,555,288),color=None,fill=P,radius=.055)
  text(p,'Market evidence',52,173,491,10,'IB',maxlines=1)
  target_top=300
  clip=fitz.Rect(40,start,555,690)
  p.show_pdf_page(fitz.Rect(40,target_top,555,target_top+clip.height),snapshot,item['page']-1,clip=clip)
  fonts(p)
  for j,a in enumerate(item['panels']):
   x=52+j*166
   if j:p.draw_line((x-8,190),(x-8,265),color=L,width=.5)
   text(p,a['title'],x,190,151,8.3,'IB',maxlines=1)
   text(p,a['unit'],x,204,151,6.5,col=M,maxlines=1)
   if a.get('kind')=='pie':
    colors=[B,(.32,.52,.88),(.53,.66,.90),(.69,.77,.92),(.83,.87,.95)]
    cx=x+26;cy=242;radius=23;angle=-90;total=sum(a['values'])
    for k,(name,v) in enumerate(zip(a['names'],a['values'])):
     frac=v/total;start=(cx+radius*math.cos(math.radians(angle)),cy+radius*math.sin(math.radians(angle)))
     sh=p.new_shape();sh.draw_sector((cx,cy),start,-frac*360,fullSector=True);sh.finish(color=W,fill=colors[k],width=.5);sh.commit();angle+=frac*360
     yy=217+k*10
     box(p,(x+57,yy+2,x+61,yy+6),colors[k])
     text(p,name,x+65,yy,61,6.5,col=M,maxlines=1)
     text(p,f'{frac*100:.1f}%',x+121,yy,32,6.5,'IB',maxlines=1)
   else:
    percent=a['unit'].startswith('%');domain=100 if percent else max(a['values'])*1.12
    for k,(year,v) in enumerate(zip(a['labels'],a['values'])):
     yy=223+k*24;text(p,year,x,yy-2,43,6.9,col=M,maxlines=1)
     barx=x+44;width=64*v/domain
     box(p,(barx,yy,barx+width,yy+9),B if k else (.71,.79,.94))
     digits=2 if 'trillion' in a['unit'] or 'billion' in a['unit'] else 1
     value=f'{v:,.{digits}f}'+('%' if percent else '')
     if country=='Iraq' and j==0 and k==1:value='~'+value
     text(p,value,barx+width+4,yy-2,45,7.1,'IB',maxlines=1)
    p.draw_line((x+44,260),(x+108,260),color=L,width=.5)
   p.insert_link({'kind':fitz.LINK_URI,'from':fitz.Rect(x,188,x+151,272),'uri':a['source']})
  text(p,item['note'],52,272,491,7,col=M,maxlines=1)
 # Remove one recognition tile and rebalance the remaining four.
 p=doc[1];clear(p,fitz.Rect(40,562,555,775),(.914,.914,.914))
 stream=BytesIO();c=Canvas(stream,pagesize=(515,172));clip=c.beginPath();clip.roundRect(0,0,515,172,8);c.clipPath(clip,stroke=0,fill=0);c.linearGradient(0,0,515,0,[HexColor('#101d80'),HexColor('#1b3fda')]);c.showPage();c.save()
 bg=fitz.open(stream=stream.getvalue(),filetype='pdf');p.show_pdf_page(fitz.Rect(40,562,555,734),bg,0)
 text(p,'RECOGNITION',52,574,491,6.5,'IB',(.73,.81,1))
 text(p,'Industry recognition',52,588,491,12,'PH',W)
 text(p,'Four awards for growth, platform services, payment facilitation and innovation in 2025 and 2026.',52,609,491,7.2,col=W)
 awards=[('Fastest Growing Fintech Company, Pakistan','Global Banking & Finance Review · 2025'),('Best PaaS Provider of the Year, FinTech','Global BankTech Awards · 2025'),('Fastest Growing Brand of the Year','Payment Facilitator category · 2025'),('Digital Payments Innovation Leader','Transform Awards · 2026')]
 for j,(title,source) in enumerate(awards):
  x=52+j*125.75;w=113.75
  p.draw_rect((x,632,x+w,721),color=(.42,.53,.91),fill=W,fill_opacity=.08,stroke_opacity=.7,width=.7,radius=.05)
  cx=x+w/2;cy=655
  p.draw_circle((cx,cy),11,color=None,fill=W)
  p.draw_polyline([(cx-4,cy-5),(cx+4,cy-5),(cx+3,cy+1),(cx+1,cy+3),(cx-1,cy+3),(cx-3,cy+1),(cx-4,cy-5)],color=B,width=.8)
  p.draw_polyline([(cx-4,cy-4),(cx-7,cy-4),(cx-6,cy),(cx-3,cy+1)],color=B,width=.8)
  p.draw_polyline([(cx+4,cy-4),(cx+7,cy-4),(cx+6,cy),(cx+3,cy+1)],color=B,width=.8)
  p.draw_line((cx,cy+3),(cx,cy+6),color=B,width=.8)
  p.draw_line((cx-4,cy+6),(cx+4,cy+6),color=B,width=.8)
  text(p,title,x+8,670,w-16,8.3,'IB',W,maxlines=4,align=True)
  text(p,source,x+8,694,w-16,6.8,col=W,maxlines=3,align=True)
