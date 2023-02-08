#!/usr/local/environments/flask/lib/python3.6
import qrcode
from PIL import Image, ImageDraw, ImageFont
from qrcode.image.styledpil import StyledPilImage
#from qrcode.image.styles.moduledrawers.pil import RoundedModuleDrawer
from qrcode.image.styles.colormasks import RadialGradiantColorMask

class QrcodeHelper:
    def gen_code(self, text, input_data):
        link = f'{input_data}'
        text = str(text)
        #print(text, input_data)
        #txt_img = 'images/txt.png'
        #Creating an instance of qrcode
        qr = qrcode.QRCode(
                version=1,
                box_size=15,
                border=2)
        qr.add_data(input_data)
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')

        img = qr.make_image(image_factory=StyledPilImage, 
                            #module_drawer=RoundedModuleDrawer(),
                            color_mask=RadialGradiantColorMask(),)
                            #embeded_image_path=txt_img)

        image1_size = img.size
        imgl = self.create_image('Link: ',link, (image1_size[0], 100), 32)
        imgt = self.create_image('Mesa: ',text, (image1_size[0], 100), 72)
        image2_size = imgt.size
        new_image = Image.new('RGB',(image1_size[0], image1_size[1] + 2*image2_size[1]), (250,250,250))
        new_image.paste(imgl,(0,0))
        new_image.paste(img,(0,image2_size[1]))
        new_image.paste(imgt,(0,image1_size[1] + image2_size[1]))


        new_image.save(f'images/{text}.png')
        return f'images/{text}.png'
    
    def create_image(self, tipo, message, size, size_t, bgColor='yellow', fontColor='black'):
        W, H = size
        #if tipo[1:4] not in message.lower():
        message = tipo + message

        font = ImageFont.truetype('arial.ttf', size_t)
        image = Image.new('RGB', size, bgColor)
        draw = ImageDraw.Draw(image)
        _, _, w, h = draw.textbbox((0, 0), message, font=font)
        draw.text(((W-w)/2, (H-h)/2), message, font=font, fill=fontColor)
        #image.save(output)
        return image
        