import qrcode
from PIL import Image, ImageDraw, ImageFont
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers.pil import RoundedModuleDrawer
from qrcode.image.styles.colormasks import RadialGradiantColorMask



def create_image(size, bgColor, message, font, fontColor):
    W, H = size
    image = Image.new('RGB', size, bgColor)
    draw = ImageDraw.Draw(image)
    _, _, w, h = draw.textbbox((0, 0), message, font=font)
    draw.text(((W-w)/2, (H-h)/2), message, font=font, fill=fontColor)
    return image

myFont = ImageFont.truetype('arial.ttf', 24)
myMessage = '102'
img = create_image((50, 50), 'yellow', myMessage, myFont, 'black')

img.save('images/hello.png')

qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=15,
    border=2,
)
qr.add_data('Some data')
#qr.make(fit=True)

#img = qr.make_image(fill_color="black", back_color="white")
#img = qr.make_image(back_color=(255, 195, 235), fill_color=(55, 95, 35))
img = qr.make_image(image_factory=StyledPilImage, 
                    module_drawer=RoundedModuleDrawer(),
                    color_mask=RadialGradiantColorMask(),
                    embeded_image_path="images/hello.png")

img.save("images/some_file2.png")