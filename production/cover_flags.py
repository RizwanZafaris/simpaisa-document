"""Replace the cover's faded flags with opaque versions from the country pages."""
import fitz

def apply(doc,H):
 p=doc[0];src=fitz.open(stream=doc.tobytes(),filetype='pdf')
 pm=src[0].get_pixmap(matrix=fitz.Matrix(4,4),alpha=False)
 # Existing cover positions and order are retained.
 for page,x in [(15,62),(13,135.5),(14,208.5),(9,282.5),(10,356),(11,435.5),(12,503.5)]:
  left=x-1;right=x+31 if page!=11 else x+19
  # The cover art has a horizontal colour field here. Match each quarter-point scanline.
  for k in range(100):
   y=500+k/4;rgb=pm.pixel(round((left-2)*4),round(y*4));p.draw_rect((left,y,right,y+.26),color=None,fill=tuple(c/255 for c in rgb))
  target=fitz.Rect(x,501,x+29,523);clip=fitz.Rect(526,16,555,38)
  if page==11:
   target=fitz.Rect(x,501,x+17,523);clip=fitz.Rect(526,16,543,38)
  p.show_pdf_page(target,src,page-1,clip=clip)
  if page==11:
   # Keep the two-pennant silhouette; do not import its dark header background.
   points=[(x,501),(x+17,512),(x+8,512),(x+17,523),(x,523)]
   cmd=' '.join(f'{xx:.3f} {p.rect.height-yy:.3f} '+('m' if i==0 else 'l') for i,(xx,yy) in enumerate(points))+' h W n\n'
   ref=p.get_contents()[-1];doc.update_stream(ref,b'q\n'+cmd.encode()+doc.xref_stream(ref)+b'\nQ')
