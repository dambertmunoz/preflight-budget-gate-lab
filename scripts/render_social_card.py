
from pathlib import Path
try:
    from PIL import Image, ImageDraw, ImageFont
except Exception as e:
    print('PIL missing', e)
    raise SystemExit(1)
W=H=1200
img=Image.new('RGB',(W,H),(14,11,38))
d=ImageDraw.Draw(img)
# gradients-ish
for r,c in [(420,(30,27,75)),(300,(21,18,55)),(180,(14,11,38))]:
    d.ellipse((980-r,145-r,980+r,145+r), fill=c)
for r,c in [(480,(38,23,70)),(330,(22,16,50)),(210,(14,11,38))]:
    d.ellipse((160-r,980-r,160+r,980+r), fill=c)

def font(size,bold=False):
    candidates = [
        '/System/Library/Fonts/Supplemental/Arial Bold.ttf' if bold else '/System/Library/Fonts/Supplemental/Arial.ttf',
        '/System/Library/Fonts/SFNS.ttf',
        '/System/Library/Fonts/Helvetica.ttc',
    ]
    for p in candidates:
        try: return ImageFont.truetype(p,size)
        except Exception: pass
    return ImageFont.load_default()

def rr(box, radius, fill, outline=None, width=1):
    d.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)

def node(x,y,w,h,label,fill=(15,23,42),outline=(125,211,252)):
    rr((x,y,x+w,y+h),22,fill,outline,3)
    tw=d.textlength(label,font=font(26,True))
    d.text((x+w/2-tw/2,y+h/2-15),label,font=font(26,True),fill=(248,250,252))

def arrow(x1,y1,x2,y2,color=(125,211,252),width=4):
    d.line((x1,y1,x2,y2),fill=color,width=width)
    # simple arrowhead
    import math
    ang=math.atan2(y2-y1,x2-x1)
    for off in [2.6,-2.6]:
        x=x2-18*math.cos(ang+off); y=y2-18*math.sin(ang+off)
        d.line((x2,y2,x,y),fill=color,width=width)

# text
d.text((80,82),'Your agent spends',font=font(58,True),fill=(248,250,252))
d.text((80,148),'before it thinks',font=font(58,True),fill=(248,250,252))
d.text((82,222),'Preflight Budget Gate for agent tools',font=font(30),fill=(186,230,253))
rr((760,80,1120,190),26,(15,23,42),(125,211,252),2)
d.text((800,118),'Dambert Muñoz',font=font(28,True),fill=(248,250,252))
d.text((800,154),'AI Architect',font=font(24),fill=(203,213,225))
rr((85,315,1115,895),42,(15,23,42),(75,120,150),2)
node(145,420,170,86,'Intent')
arrow(315,463,430,463)
node(430,420,170,86,'Policy')
arrow(600,463,705,463)
node(705,420,175,86,'Reserve')
arrow(792,506,792,612)
rr((683,612,903,710),28,(14,11,38),(167,139,250),4)
d.text((760,630),'Gate',font=font(30,True),fill=(248,250,252))
d.text((718,670),'side_effect_allowed?',font=font(20,True),fill=(203,213,225))
arrow(903,662,1005,662)
rr((1005,619,1077,705),18,(20,60,80),(125,211,252),3)
d.text((1018,648),'OK',font=font(24,True),fill=(248,250,252))
d.text((964,746),'Execute',font=font(20,True),fill=(203,213,225))
arrow(792,710,595,792,(167,139,250),4)
rr((392,746,597,828),22,(42,30,75),(167,139,250),3)
d.text((426,775),'Manual Review',font=font(24,True),fill=(248,250,252))
arrow(683,662,515,584,(167,139,250),4)
rr((410,538,525,608),20,(42,30,75),(167,139,250),3)
d.text((442,558),'Deny',font=font(25,True),fill=(248,250,252))
rr((135,922,1065,1054),30,(15,23,42),(60,70,90),2)
d.text((170,962),'Audit trace',font=font(28,True),fill=(203,213,225))
d.text((170,1010),'HELD → COMMITTED / RELEASED · stable DecisionCode · no side effect before admission',font=font(22,True),fill=(203,213,225))
d.text((80,1128),'dambertmunoz.com · linkedin.com/in/dambert-m-4b772397',font=font(23),fill=(203,213,225))
path=Path('assets/preflight-budget-gate-social-card.png')
img.save(path)
print(path)
