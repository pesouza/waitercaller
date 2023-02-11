#!/usr/local/environments/flask/lib/python3.6
import qrcode
from PIL import Image, ImageDraw, ImageFont
from qrcode.image.styledpil import StyledPilImage
#from qrcode.image.styles.moduledrawers.pil import RoundedModuleDrawer
from qrcode.image.styles.colormasks import RadialGradiantColorMask
from os.path import join, dirname, realpath

IMAGES_PATH = join(dirname(realpath(__file__)), 'static', 'images')

class QrcodeHelper:
    def gen_code(self, text, input_data):
        #link = f'{input_data}'
        link = '\xa9 waiterexpress.com.br'
        text = str(text)
 
        #Creating an instance of qrcode
        qr = qrcode.QRCode(
                version=1,
                box_size=15,
                border=2)
        qr.add_data(input_data)
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')

        img = qr.make_image(image_factory=StyledPilImage, 
                            color_mask=RadialGradiantColorMask())
    
        image1_size = img.size
        imgc = self.create_image('Chame o', (image1_size[0], 100), 72)
        imgw = self.create_image('Garçom!', (image1_size[0], 100), 72, 'ariblk')
        imgl = self.create_image(link, (image1_size[0], 100), 28)
        imgt = self.create_image(text, (image1_size[0], 100), 72, 'ariblk')
        image2_size = imgt.size
        new_image = Image.new('RGB',(image1_size[0], image1_size[1] + 4*image2_size[1]), (250,250,250))
        new_image.paste(imgc,(0, 0))
        new_image.paste(imgw,(0, image2_size[1]))
        new_image.paste(img,(0, 2*image2_size[1]))
        new_image.paste(imgl,(0, image1_size[1] + 2*image2_size[1]))
        new_image.paste(imgt,(0,image1_size[1] + 3*image2_size[1]))

        new_image.save(f'{IMAGES_PATH}/{link[15:]}.png')
        return f'images/{link[15:]}.png'
    
    def create_image(self, message, size, size_t, font= 'arial',
                     bgColor='yellow', fontColor='black'):
        W, H = size
        font = ImageFont.truetype(font + '.ttf', size_t)
        image = Image.new('RGB', size, bgColor)
        draw = ImageDraw.Draw(image)
        _, _, w, h = draw.textbbox((0, 0), message, font=font)
        draw.text(((W-w)/2, (H-h)/2), message, font=font, fill=fontColor)
        #image.save(output)
        return image
        