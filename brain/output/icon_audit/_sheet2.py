from PIL import Image, ImageDraw
import os
d="/Users/christopherfryman/Documents/code/AOP MAP/brain/output/icon_audit/svgs"
order=["z_Region","z_Park","z_Pavilion","p_Topo","p_Trace","p_Tree","t_Search","t_Hot","t_Cal","u_Locate","u_Install","fab_Pencil"]
H=150; pad=16; lab=20
imgs=[]
for n in order:
    p=os.path.join(d,n+".png")
    if not os.path.exists(p): imgs.append((n,None)); continue
    im=Image.open(p).convert("RGBA")
    bg=Image.new("RGBA",im.size,(245,239,224,255)); bg.alpha_composite(im); im=bg.convert("RGB")
    r=H/im.size[1]; im=im.resize((int(im.size[0]*r),H)); imgs.append((n,im))
W=sum((im.size[0] if im else 90)+pad for _,im in imgs)+pad
sheet=Image.new("RGB",(W,H+pad*2+lab),(245,239,224)); dr=ImageDraw.Draw(sheet)
x=pad
for n,im in imgs:
    w=im.size[0] if im else 90
    if im: sheet.paste(im,(x,pad))
    dr.text((x,pad+H+4),n,fill=(60,45,30))
    x+=w+pad
o="/Users/christopherfryman/Documents/code/AOP MAP/brain/output/icon_audit/all_icons.png"
sheet.save(o); print("saved",o,sheet.size)
