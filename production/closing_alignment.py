"""Center the closing headline by visible letter bounds, preserving the background."""
import fitz
from PIL import Image

def apply(doc,H):
 p=doc[18];texts=['Let’s connect','more markets.'];size=37
 # Measure glyph ink, rather than the font's unequal side bearings.
 temp=fitz.open();q=temp.new_page(width=p.rect.width,height=p.rect.height)
 q.draw_rect(q.rect,color=None,fill=(0,0,0));q.insert_font(fontname='PH',fontfile=str(H/'fonts/Poppins.ttf'))
 boxes=[]
 for t,y in zip(texts,[410,458]):
  q.insert_text((150,y),t,fontname='PH',fontsize=size,color=(1,1,1))
  clip=fitz.Rect(130,y-40,470,y+8);pm=q.get_pixmap(matrix=fitz.Matrix(4,4),clip=clip,alpha=False)
  im=Image.frombytes('RGB',[pm.width,pm.height],pm.samples).convert('L').point(lambda v:255 if v>230 else 0)
  x0,y0,x1,y1=im.getbbox();boxes.append(fitz.Rect(clip.x0+x0/4,clip.y0+y0/4,clip.x0+x1/4,clip.y0+y1/4))
 dy=p.rect.height/2-(boxes[0].y0+boxes[1].y1)/2
 for t in texts:
  for r in p.search_for(t):p.add_redact_annot(r,fill=False,cross_out=False)
 p.apply_redactions(images=0,graphics=0,text=0)
 p.insert_font(fontname='PH',fontfile=str(H/'fonts/Poppins.ttf'))
 for t,y,b in zip(texts,[410,458],boxes):
  x=150+p.rect.width/2-(b.x0+b.x1)/2
  p.insert_text((x,y+dy),t,fontname='PH',fontsize=size,color=(1,1,1))
