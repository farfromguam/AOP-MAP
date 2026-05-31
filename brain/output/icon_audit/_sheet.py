from PIL import Image, ImageDraw
import os
base="/Users/christopherfryman/Documents/code/AOP MAP/brain/output/icon_audit/cells"
order=["zoomRegion","zoomPark","zoomPavilion","presetPark","presetTopo","presetTrace","presetSatellite","lrTabSearch","lrTabHot","lrTabCal"]
cell=170; pad=14; lab=22
sheet=Image.new("RGB",(len(order)*(cell+pad)+pad, cell+pad*2+lab),(245,239,224))
d=ImageDraw.Draw(sheet)
for i,name in enumerate(order):
    p=os.path.join(base,name+".png")
    if not os.path.exists(p): continue
    im=Image.open(p).convert("RGB"); im.thumbnail((cell,cell))
    x=pad+i*(cell+pad); y=pad
    sheet.paste(im,(x+(cell-im.size[0])//2, y+(cell-im.size[1])//2))
    short=name.replace("preset","p:").replace("zoom","z:").replace("lrTab","t:")
    d.text((x+4,y+cell+4),short,fill=(60,45,30))
out="/Users/christopherfryman/Documents/code/AOP MAP/brain/output/icon_audit/contact_sheet.png"
sheet.save(out); print("saved",out, sheet.size)
