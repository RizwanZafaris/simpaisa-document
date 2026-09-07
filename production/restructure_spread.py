"""Page 7 market matrix; page 8 portrait digital-market overview."""
from pathlib import Path
import fitz,json
H=Path(__file__).resolve().parent
src=fitz.open(H/'build/Simpaisa_Network_Playbook_2026_Complete.pdf');out=fitz.open()
F={k:fitz.Font(fontfile=str(H/'fonts'/v)) for k,v in [('IR','Inter.ttf'),('IB','InterSemi.ttf'),('PH','Poppins.ttf')]}
N=(0,.094,.4);B=(.004,.337,.984);M=(.32,.39,.50);W=(1,1,1);G=(.914,.914,.914);P=(.925,.949,.984);L=(.82,.86,.94)
log=[]
def setup(p):
 for k,v in [('IR','Inter.ttf'),('IB','InterSemi.ttf'),('PH','Poppins.ttf')]:p.insert_font(fontname=k,fontfile=str(H/'fonts'/v))
def text(p,t,x,y,w,size=9,font='IR',color=N,maxh=60):
 lines=[];line=''
 for word in t.split():
  q=(line+' '+word).strip()
  if F[font].text_length(q,fontsize=size)>w:lines.append(line);line=word
  else:line=q
 lines.append(line);h=len(lines)*size*1.28
 assert h<=maxh+.5,(t,h,maxh)
 for i,l in enumerate(lines):p.insert_text((x,y+F[font].ascender*size+i*size*1.28),l,fontname=font,fontsize=size,color=color)
 log.append({'page':p.number+1,'text':t,'rect':[x,y,x+w,y+h]});return h
def center(p,t,x,y,w,size=9,color=N):text(p,t,x+(w-F['IB'].text_length(t,fontsize=size))/2,y,w,size,'IB',color)
def box(p,r,c):p.draw_rect(r,color=None,fill=c)
def metric_icon(p,kind,x,y):
 # Native vector symbols share stroke weight and an 18-point box.
 def ln(a,b):p.draw_line((x+a[0],y+a[1]),(x+b[0],y+b[1]),color=W,width=1.1)
 def circle(cx,cy,r):p.draw_circle((x+cx,y+cy),r,color=W,width=1.1)
 if kind==0:
  circle(8,5,2.5);circle(15,6,2)
  p.draw_bezier((x+2,y+16),(x+2,y+8),(x+13,y+8),(x+13,y+16),color=W,width=1.1)
  p.draw_bezier((x+13,y+10),(x+17,y+9),(x+19,y+12),(x+19,y+16),color=W,width=1.1)
 elif kind==1:
  circle(10,9,8);p.draw_oval((x+6,y+1,x+14,y+17),color=W,width=1)
  ln((2,9),(18,9))
 elif kind==2:
  p.draw_rect((x+5,y+1,x+15,y+18),color=W,width=1.1)
  ln((8,4),(12,4));ln((9,15),(11,15))
 else:
  p.draw_rect((x+2,y+10,x+18,y+17),color=W,width=1.1)
  ln((5,10),(3,2));ln((15,10),(17,2));circle(6,13.5,.65);circle(10,13.5,.65)
def footer(p,n,width,height):
 p.draw_line((40,height-48),(width-40,height-48),color=(.78,.78,.78),width=.6)
 text(p,'www.simpaisa.com',40,height-39,200,7.5,color=(.4,.4,.4));text(p,f'{n:02}',width-52,height-39,20,7.5,color=(.4,.4,.4))
names=['Pakistan','Bangladesh','Nepal','Iraq','Egypt','Saudi Arabia','Nigeria'];flags=[]
for i in range(7):flags.append(src[7].get_pixmap(matrix=fitz.Matrix(4,4),clip=fitz.Rect(69,175+i*46,84,187+i*46)).tobytes('png'))
data=json.loads((H/'network-market-data.json').read_text());cov=[[1,1,1],[1,1,1],[1,1,1],[1,0,0],[1,1,1],[1,1,0],[1,1,1]]
for idx in range(19):
 if idx not in [6,7]:out.insert_pdf(src,from_page=idx,to_page=idx);continue
 if idx==6:
  p=out.new_page(width=595,height=842);setup(p);box(p,(0,0,595,842),G)
  text(p,'The Gap We Close',40,39,515,20,'PH')
  text(p,'Across these seven markets, customers pay from wallets and bank accounts as well as local cards. When these methods are missing at checkout, businesses risk losing the sale and the customer. Simpaisa connects these local methods through one integration.',40,76,515,9.5,maxh=55)
  text(p,'Market context and service coverage',40,132,300,10.5,'IB')
  text(p,'A: acceptance   D: disbursements   R: remittance',320,135,235,7,color=M)
  xs=[40,113,211,309,407,505,555];heads=['MARKET','WALLET BASE','BANK TRANSFERS','DOMESTIC CARD SCHEME','PAYOUT RAILS','COVERAGE'];box(p,(40,158,555,182),(0.11,.11,.11))
  for j,h in enumerate(heads):
   # Wrap long headings, then centre the complete block in its column.
   width=xs[j+1]-xs[j];sz=6.4
   lines=['DOMESTIC CARD','SCHEME'] if j==3 else [h]
   line_height=8.2
   baseline=170 + (F['IB'].ascender+F['IB'].descender)*sz/2 - (len(lines)-1)*line_height/2
   for k,line in enumerate(lines):
    center(p,line,xs[j],baseline+k*line_height-F['IB'].ascender*sz,width,sz,W)
  for i,row in enumerate(data['rows']):
   y=182+i*58;box(p,(40,y,555,y+58),W if i%2 else P)
   p.insert_image((70,y+13,83,y+23),stream=flags[i]);center(p,names[i],40,y+32,73,7.3)
   for j,val in enumerate(row):
    x=xs[j+1];yy=y+21
    for k,part in enumerate(val.split('\n')):
     if k==0:
      sz=10 if part[0].isdigit() or part.startswith('~') else 8.6
      while F['IB'].text_length(part,fontsize=sz)>82 and sz>8:sz-=.2
      text(p,part,x+8,y+17-F['IB'].ascender*sz,82,sz,'IB',B if part[0].isdigit() or part.startswith('~') else N,maxh=44)
     else:
      # Keep the reporting period together on its own line; no dangling separators.
      for segment in part.split(' | '):
       yy+=text(p,segment,x+8,yy,82,7.8,'IR',M,maxh=40)
    assert yy<=y+53,(i,j,yy,y)
    u=data['cell_sources'].get(f'{i},{j}')
    if u:p.insert_link({'kind':fitz.LINK_URI,'from':fitz.Rect(x,y,x+98,y+58),'uri':u})
   for j,on in enumerate(cov[i]):
    x=509+j*15;box(p,(x,y+23,x+12,y+35),B if on else (.88,.9,.93))
    sz=6.7;baseline=y+29+(F['IB'].ascender+F['IB'].descender)*sz/2
    center(p,'ADR'[j],x,baseline-F['IB'].ascender*sz,12,sz,W if on else (.61,.65,.73))
   p.draw_line((40,y+58),(555,y+58),color=L,width=.5)
   for edge in xs[1:-1]:p.draw_line((edge,y),(edge,y+58),color=L,width=.25)
  text(p,'Market figures come from central banks, regulators and official industry sources and reflect accounts, users, transfer activity or access as labelled, with reporting periods varying by market. These are market totals, not Simpaisa volumes; coverage indicates Simpaisa’s available services.',40,602,515,8,color=M,maxh=34)
  # Match page 4: one rounded gradient panel with centred inset coverage cards.
  from io import BytesIO
  from reportlab.pdfgen.canvas import Canvas
  from reportlab.lib.colors import HexColor
  stream=BytesIO();canvas=Canvas(stream,pagesize=(515,136))
  clip=canvas.beginPath();clip.roundRect(0,0,515,136,8)
  canvas.clipPath(clip,stroke=0,fill=0)
  canvas.linearGradient(0,0,515,0,[HexColor('#101d80'),HexColor('#1b3fda')])
  canvas.showPage();canvas.save()
  bg=fitz.open(stream=stream.getvalue(),filetype='pdf')
  p.show_pdf_page(fitz.Rect(40,648,555,784),bg,0)
  text(p,'SIMPAISA COVERAGE',52,658,491,6.7,'IB',(.73,.80,1))
  text(p,'The problem we solve',52,672,491,12,'PH',W)
  text(p,'International businesses cannot efficiently integrate, govern, settle and operate dozens of fragmented local payment systems country by country.',52,692,491,9.5,color=W,maxh=30)
  for j,(value,label) in enumerate([(7,'Acceptance markets'),(6,'Disbursement markets'),(5,'Remittance markets')]):
   x=52+j*167
   p.draw_rect((x,729,x+157,772),color=(.42,.53,.91),fill=W,width=.8,fill_opacity=.09,stroke_opacity=.7,radius=.16)
   center(p,str(value),x,732,157,19,W)
   center(p,label,x,758,157,7.6,W)
  footer(p,7,595,842)
 else:
  p=out.new_page(width=595,height=842);setup(p);box(p,(0,0,595,842),G)
  text(p,'Seven markets going digital',40,39,515,20,'PH')
  text(p,'Population and digital access show the scale of the opportunity. Payment adoption shows how that reach translates into everyday transactions.',40,76,515,9.5,maxh=42)
  text(p,'Market scale and connectivity',40,121,515,11,'IB')
  xs=[40,149,284.333333,419.666667,555];box(p,(40,144,555,205),N)
  for j,(label,unit) in enumerate([('MARKET',''),('POPULATION','2025 | millions'),('INTERNET USE','2024 | % of people'),('MOBILE CONNECTIONS','2024 | per 100 people')]):
   if j:metric_icon(p,j-1,(xs[j]+xs[j+1])/2-10,153)
   center(p,label,xs[j],178,xs[j+1]-xs[j],7,W)
   if unit:text(p,unit,(xs[j]+xs[j+1]-F['IR'].text_length(unit,fontsize=6.8))/2,192,xs[j+1]-xs[j]-20,6.8,color=(.73,.81,1),maxh=12)
  d=json.loads((H/'digital-market-data.json').read_text())
  for i,row in enumerate(d['rows']):
   y=205+32*i;box(p,(40,y,555,y+32),W if i%2==0 else P)
   p.insert_image((49,y+10,62,y+20),stream=flags[i]);text(p,names[i],69,y+10,78,7.6,'IB')
   for j,ind in enumerate(['SP.POP.TOTL','IT.NET.USER.ZS','IT.CEL.SETS.P2']):
    value=row['metrics'][ind]['value'];v=value/1e6 if j==0 else value;x=xs[j+1]+10
    center(p,f'{v:.1f}'+('%' if j==1 else ''),xs[j+1],y+4,xs[j+2]-xs[j+1],11,B)
    w=xs[j+2]-xs[j+1]-20;box(p,(x,y+24,x+w,y+26),(.85,.89,.96));box(p,(x,y+24,x+w*v/[300,100,180][j],y+26),B)
    p.insert_link({'kind':fitz.LINK_URI,'from':fitz.Rect(xs[j+1],y,xs[j+2],y+32),'uri':d['sources'][ind]})
  text(p,'Source: World Bank / ITU, using the existing playbook dataset. Mobile connections are subscriptions, not unique people. Bar scales differ by column.',40,439,515,7,color=M,maxh=25)
  text(p,'Digital payment growth',40,475,515,11,'IB')
  text(p,'Selected payment indicators, with the measure, reporting period and source shown.',40,495,515,8.5,color=M)
  growth=json.loads((H/'payment-growth-data.json').read_text())['rows']
  box(p,(40,518,555,756),W)
  for i,row in enumerate(growth):
   y=518+i*34
   p.insert_image((49,y+12,62,y+22),stream=flags[i]);text(p,row['country'],69,y+12,78,7.6,'IB')
   text(p,row['labels'][0],166,y+4,48,10,'IB',M)
   text(p,row['labels'][1],355,y+4,62,10,'IB',B)
   domain=100 if row.get('kind')=='share' else row['after']*1.12
   box(p,(219,y+11,341,y+14),(.85,.89,.96))
   box(p,(219,y+11,219+122*row['after']/domain,y+14),B)
   p.draw_line((219+122*row['before']/domain,y+8),(219+122*row['before']/domain,y+17),color=N,width=1)
   text(p,row['caption'],166,y+21,379,6.4,color=M,maxh=10)
   change=f"+{row['growth']:.0f} pp" if row.get('kind')=='share' else f"+{row['growth']:.1f}%"
   center(p,change,420,y+4,125,13,B)
   p.insert_link({'kind':fitz.LINK_URI,'from':fitz.Rect(149,y,555,y+34),'uri':row['source']})
   if i<6:p.draw_line((49,y+34),(545,y+34),color=L,width=.4)
  text(p,'Bars show later levels; markers show earlier levels. Scales and periods differ by row. Growth uses reported figures; pp means percentage points. Selected indicators, not a ranking.',40,766,515,7,color=M,maxh=24)
  footer(p,8,595,842)
# Pakistan evidence: one statistic each for wallets, PayPak and Raast.
p=out[8]
area=fitz.Rect(46,186,549,287)
for link in p.get_links():
 if fitz.Rect(link['from']).intersects(area):p.delete_link(link)
p.add_redact_annot(area,fill=(.943,.957,1),cross_out=False)
p.apply_redactions(images=0,graphics=0,text=0);setup(p)
for j,item in enumerate(json.loads((H/'pakistan-evidence-data.json').read_text())['rows']):
 x=48+j*169.953125
 if j:p.draw_line((x-8,190),(x-8,267),color=L,width=.6)
 text(p,item['title'],x,190,151,8.4,'IB',N)
 text(p,item['value'],x,208,151,23,'IB',B)
 text(p,item['label'],x,240,151,8,'IR',N)
 text(p,item['period'],x,257,151,6.8,'IR',M)
 p.insert_link({'kind':fitz.LINK_URI,'from':fitz.Rect(x,188,x+151,269),'uri':item['url']})
text(p,'Sources: easypaisa digital bank, 1LINK and State Bank of Pakistan. Market figures, not Simpaisa volumes.',48,277,499,6.2,color=M,maxh=10)
# Bangladesh: lead market evidence with the existing credit-card value shares.
p=out[9];area=fitz.Rect(46,186,378,273)
for link in p.get_links():
 if fitz.Rect(link['from']).intersects(area):p.delete_link(link)
p.add_redact_annot(area,fill=(.943,.957,1),cross_out=False)
p.apply_redactions(images=0,graphics=0,text=0);setup(p)
text(p,'Credit-card value share',48,190,155,8.4,'IB')
text(p,'March 2025 | selected schemes',48,203,155,6.8,color=M)
for j,(label,value) in enumerate([('Visa',71.8),('Mastercard',17.5)]):
 y=221+j*24
 text(p,label,48,y-2,49,7.2,color=M)
 box(p,(102,y,102+value*.72,y+9),B if j==0 else (.72,.80,.96))
 text(p,f'{value:.1f}%',107+value*.72,y-2,42,7.2,'IB')
for value in [0,50,100]:text(p,str(value),100+value*.72,260,22,6.2,color=M)
p.draw_line((102,258),(174,258),color=L,width=.5)
text(p,'Mobile financial services (BDT tn)',218,190,155,8.4,'IB')
text(p,'+7.5%',339,203,35,7.5,'IB',B)
for j,(label,value) in enumerate([('2024',17.4),('2025',18.7)]):
 y=221+j*24
 text(p,label,218,y-2,27,7.2,color=M)
 box(p,(248,y,248+value*4.5,y+9),B if j else (.72,.80,.96))
 text(p,str(value),253+value*4.5,y-2,30,7.2,'IB')
for value in [0,10,20]:text(p,str(value),246+value*4.5,260,22,6.2,color=M)
p.draw_line((248,258),(338,258),color=L,width=.5)
from regional_evidence import apply as apply_regional_evidence
apply_regional_evidence(out,H)
from closing_alignment import apply as align_closing
align_closing(out,H)
path=H/'build/Simpaisa_Network_Playbook_2026_Spread.pdf';out.save(path,garbage=4,deflate=True)
(H/'build/spread-layout-log.json').write_text(json.dumps(log,indent=2));print(path)
