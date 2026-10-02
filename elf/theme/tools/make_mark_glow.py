"""The PS2 mark's glow (gfx/ripps2_mark_glow.png): the mark's own shape, padded and blurred, white on
transparency so the draw call tints it. RIPPS2 breathes it over the mark while something is loading.

    python make_mark_glow.py <mark.png>

Give it a large render of the category mark (make_category_mark.py at 384 px). The glow is padded to
1.25 x the mark's width and 108/44 of its height, the proportions RIPPS2 draws it at, centred on the mark.
"""
import sys
from PIL import Image, ImageFilter

mark = Image.open(sys.argv[1]).convert('RGBA')
w, h = mark.size
pad_x = int(round(w * 0.125))
pad_y = int(round((h * 108.0 / 44.0 - h) / 2))
alpha = Image.new('L', (w + 2 * pad_x, h + 2 * pad_y), 0)
alpha.paste(mark.split()[3], (pad_x, pad_y))
glow = alpha.filter(ImageFilter.GaussianBlur(w / 40.0)).point(lambda v: min(255, int(v * 1.8)))
glow = glow.resize((glow.size[0] // 2, glow.size[1] // 2), Image.LANCZOS)  # a glow needs no detail
out = Image.new('RGBA', glow.size, (255, 255, 255, 0))
out.putalpha(glow)
out.save('gfx/ripps2_mark_glow.png', optimize=True)
print('gfx/ripps2_mark_glow.png', out.size)
