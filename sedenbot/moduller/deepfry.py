# Copyright (C) 2020 TeamDerUntergang.
#
# SedenUserBot is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SedenUserBot is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

# Deepfry modülü kaynak kodu: https://github.com/Ovyerus/deeppyer
# @NaytSeyd tarafından portlanmıştır.

import io

from random import randint, uniform
from PIL import Image, ImageEnhance, ImageOps
from telethon import events
from telethon.tl.types import DocumentAttributeFilename

from sedenbot import bot, CMD_HELP
from sedenbot.events import sedenify

@sedenify(pattern="^.deepfry(?: |$)(.*)", outgoing=True) 
async def deepfryer(event):
    try:
        frycount = int(event.pattern_match.group(1))
        if frycount < 1:
            raise ValueError
    except:
        frycount = 1
    
    MAX_LIMIT = 5
    if frycount > MAX_LIMIT:
        frycount = MAX_LIMIT

    if event.is_reply:
        reply_message = await event.get_reply_message()
        data = await check_media(reply_message)

        if isinstance(data, bool):
            await event.edit("`Bunu deepfry yapamam!`")
            return
    else:
        await event.edit("`Deepfry yapmam için bir resme veya çıkartmaya cevap verin!`")
        return

    # Fotoğrafı (yüksek çözünürlük) bayt dizisi olarak indir
    await event.edit("`Medya indiriliyor...`")
    image = io.BytesIO()
    await event.client.download_media(data, image)
    image = Image.open(image)

    # Resime uygula
    await event.edit("`Medyaya deepfry uygulanıyor...`")
    for _ in range(frycount):
        image = await deepfry(image)

    fried_io = io.BytesIO()
    fried_io.name = "image.jpeg"
    image.save(fried_io, "JPEG")
    fried_io.seek(0)

    await event.reply(file=fried_io)


async def deepfry(img: Image) -> Image:
    colours = (
        (randint(50, 200), randint(40, 170), randint(40, 190)),
        (randint(190, 255), randint(170, 240), randint(180, 250))
    )

    img = img.copy().convert("RGB")

    # Resim formatı ayarla
    img = img.convert("RGB")
    width, height = img.width, img.height
    img = img.resize((int(width ** uniform(0.8, 0.9)), int(height ** uniform(0.8, 0.9))), resample=Image.LANCZOS)
    img = img.resize((int(width ** uniform(0.85, 0.95)), int(height ** uniform(0.85, 0.95))), resample=Image.BILINEAR)
    img = img.resize((int(width ** uniform(0.89, 0.98)), int(height ** uniform(0.89, 0.98))), resample=Image.BICUBIC)
    img = img.resize((width, height), resample=Image.BICUBIC)
    img = ImageOps.posterize(img, randint(3, 7))

    # Renk yerleşimi oluştur
    overlay = img.split()[0]
    overlay = ImageEnhance.Contrast(overlay).enhance(uniform(1.0, 2.0))
    overlay = ImageEnhance.Brightness(overlay).enhance(uniform(1.0, 2.0))

    overlay = ImageOps.colorize(overlay, colours[0], colours[1])

    # Kırmızı ve sarıyı ana görüntüye yerleştir ve keskinleştir
    img = Image.blend(img, overlay, uniform(0.1, 0.4))
    img = ImageEnhance.Sharpness(img).enhance(randint(5, 300))

    return img


async def check_media(reply_message):
    if reply_message and reply_message.media:
        if reply_message.photo:
            data = reply_message.photo
        elif reply_message.document:
            if DocumentAttributeFilename(file_name='AnimatedSticker.tgs') in reply_message.media.document.attributes:
                return False
            if reply_message.gif or reply_message.video or reply_message.audio or reply_message.voice:
                return False
            data = reply_message.media.document
        else:
            return False
    else:
        return False

    if not data or data is None:
        return False
    else:
        return data

CMD_HELP.update({
    "deepfry":
    ".deepfry [numara 1-5]\
    \nKullanım: Belirlenen görüntüye deepfry efekti uygular."
})
