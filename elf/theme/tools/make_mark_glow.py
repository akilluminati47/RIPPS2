"""The PS2 mark's glow (gfx/ripps2_mark_glow.png): the mark's own shape, padded and blurred, white on
transparency so the draw call tints it. RIPPS2 breathes it over the mark while something is loading.
The padding is a fifth of the mark on each side, so the glow draws at 1.25x the mark's width and
(44 + 2 * 32) / 44 of its height, centred on it."""
from PIL import Image, ImageFilter

PAD_X, PAD_Y = 32, 32
mark = Image.open('gfx/ripps2_mark.png').convert('RGBA')
w, h = mark.size
alpha = Image.new('L', (w + 2 * PAD_X, h + 2 * PAD_Y), 0)
alpha.paste(mark.split()[3], (PAD_X, PAD_Y))
glow = alpha.filter(ImageFilter.GaussianBlur(7)).point(lambda v: min(255, int(v * 1.8)))
out = Image.new('RGBA', alpha.size, (255, 255, 255, 0))
out.putalpha(glow)
out.save('gfx/ripps2_mark_glow.png', optimize=True)
print('gfx/ripps2_mark_glow.png', out.size)
