from PIL import Image, ImageFont, ImageDraw
from datetime import datetime
import pytz

timezone = pytz.timezone('Europe/Moscow')


def fake_qiwi_balance(balance):
    text = balance + " ₽"
    qiwi = Image.open("resources/patterns/qiwi_balance.png")
    fnt = ImageFont.truetype("resources/fonts/Roboto-Bold.ttf", 100)
    W = 1080
    w, h = fnt.getsize(text)

    d = ImageDraw.Draw(qiwi)
    d.text(((W - w) / 2, 385), text, font=fnt, fill=(255, 255, 255, 255))
    del d

    qiwi.save('resources/latest_balance.png', 'PNG')
    qiwi.show()
    return open('resources/latest_balance.png', 'rb')


def fake_qiwi_transfer(money, number):
    number = f'+{number}'
    text = f'+ {money} ₽'
    qiwi = Image.open('resources/patterns/qiwi_transfer.png')
    font_bold = ImageFont.truetype('resources/fonts/Roboto-Bold.ttf', 56)
    font_regular = ImageFont.truetype('resources/fonts/Roboto-Regular.ttf', 45)
    font_regular_phone = ImageFont.truetype('resources/fonts/Roboto-Regular.ttf', 40)
    font_time = ImageFont.truetype('resources/fonts/SourceSansPro-SemiBold.ttf', 45)
    W = 1080
    w1, h1 = font_bold.getsize(text)

    d = ImageDraw.Draw(qiwi)
    now = datetime.now(timezone)
    d.text((35, 33), f'{now.strftime("%H:%M")}', font=font_time, fill=(239, 239, 239, 255))
    d.text(((W - w1 - 40) / 2, 845), number, font=font_regular_phone, fill=(153, 153, 153, 255))
    d.text((56, 1485), now.strftime("%d.%m.%Y в %H:%M"), font=font_regular, fill=(33, 33, 33, 255))
    d.text(((W - w1) / 2, 910), text, font=font_bold, fill=(75, 189, 93, 255))
    d.text((56, 1663.5), f'{money} ₽', font=font_regular, fill=(33, 33, 33, 255))
    d.text((56, 2020), f'{money} ₽', font=font_regular, fill=(33, 33, 33, 255))

    qiwi.save('resources/latest_transfer.png', 'PNG')
    return open('resources/latest_transfer.png', 'rb')