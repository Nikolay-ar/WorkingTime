# install PIL :  pip install Pillow
# install infi.systray : pip install infi.systray

from infi.systray import SysTrayIcon
from PIL import Image, ImageDraw,ImageFont
import time

image= "pil_text.ico"
n=1
while True:
    # create image
    img = Image.new('RGBA', (50, 50), color = (255, 255, 255, 90))  # color background =  white  with transparency
    d = ImageDraw.Draw(img)
    d.rectangle([(0, 40), (50, 50)], fill=(39, 112, 229), outline=None)  #  color = blue

    #add text to the image
    font_type  = ImageFont.truetype("arial.ttf", 25)
    a= n*10
    b = n*20
    d.text((0,0), f"{a}\n{b}", fill=(255,255,0), font = font_type)

    img.save(image)


    # display image in systray 
    if n==1:
        systray = SysTrayIcon(image, "Systray")
        systray.start()
    else:
        systray.update(icon=image)
    time.sleep(5)
    n+=1
systray.shutdown()