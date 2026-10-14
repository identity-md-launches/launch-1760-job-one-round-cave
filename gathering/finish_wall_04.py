#!/usr/bin/env python3
"""One-time pigment composition; inputs have fixed ancestor/generated roles."""
import hashlib
import json
from pathlib import Path

from image_bytes import jpeg, png, read_png, resize

ROOT = Path(__file__).resolve().parent.parent
ANCESTOR = '0dd7fd645cc7f07053ecf389afd7ae96c75edd0dfc1f113e3c8e80a6cf930500'


def main():
    path = ROOT / 'artifacts/gathering/wall.png'
    target = ROOT / 'artifacts/gathering/wall-v4.png'
    old_bytes = path.read_bytes()
    if hashlib.sha256(old_bytes).hexdigest() != ANCESTOR:
        raise ValueError('wall.png must be the verified gathering 03 ancestor')
    w, h, old = read_png(old_bytes)
    gw, gh, generated = read_png(target.read_bytes())
    if (w, h) != (1254, 1254) or (gw, gh) != (1254, 1254):
        raise ValueError('unexpected image-tool or ancestor dimensions')
    final = bytearray(old)
    # Vacant stone above-left of the ancestor Pepe; no ancestor pigment occupies it.
    x0, y0, width, height = 395, 170, 140, 140
    changed = 0
    bounds = [w, h, 0, 0]
    for dy in range(height):
        for dx in range(width):
            x, y = x0 + dx, y0 + dy
            index = (y*w+x)*3
            rock = old[index:index+3]
            # Preserve deep cracks exactly, even where the small addition crosses.
            if max(rock) < 80:
                continue
            sx0, sx1 = 25+dx*1205//width, 25+(dx+1)*1205//width
            sy0, sy1 = 25+dy*1205//height, 25+(dy+1)*1205//height
            pigment = [0, 0, 0]
            coverage = 0
            for sy in range(sy0, sy1):
                for sx in range(sx0, sx1):
                    start = (sy*gw+sx)*3
                    r, g, b = generated[start:start+3]
                    charcoal = r < 105 and g < 100 and b < 90
                    ochre = r > 85 and g < r*.80 and b < r*.57
                    if charcoal or ochre:
                        color = (49, 37, 24) if charcoal else (157, 69, 30) if g < r*.64 else (165, 116, 47)
                        coverage += 1
                        for c in range(3):
                            pigment[c] += color[c]
            if not coverage:
                continue
            area = (sx1-sx0)*(sy1-sy0)
            alpha = .82*coverage/area
            light = min(1.1, max(.55, sum(rock)/(3*135)))
            for c in range(3):
                ink = pigment[c]/coverage*light
                final[index+c] = round(rock[c]*(1-alpha)+ink*alpha)
            if final[index:index+3] != rock:
                changed += 1
                bounds = [min(bounds[0], x), min(bounds[1], y),
                          max(bounds[2], x), max(bounds[3], y)]
    if changed < 1000:
        raise ValueError('insufficient new pigment')
    # Every pixel outside the vacant rectangle is demonstrably identical.
    for y in range(h):
        if y0 <= y < y0+height:
            assert final[y*w*3:(y*w+x0)*3] == old[y*w*3:(y*w+x0)*3]
            assert final[(y*w+x0+width)*3:(y+1)*w*3] == old[(y*w+x0+width)*3:(y+1)*w*3]
        else:
            assert final[y*w*3:(y+1)*w*3] == old[y*w*3:(y+1)*w*3]
    encoded = png(w, h, final)
    target.write_bytes(encoded)
    path.write_bytes(encoded)
    quality = 52
    thumb = resize(w, h, final)
    preview = jpeg(512, 512, thumb, quality)
    while len(preview) >= 100000 and quality > 10:
        quality -= 5
        preview = jpeg(512, 512, thumb, quality)
    if len(preview) >= 100000:
        raise ValueError('preview too large')
    (ROOT / 'dist/gathering/04.jpg').write_bytes(preview)
    review = {'ancestorSha256': ANCESTOR, 'ancestorSize': [w, h],
              'wallSize': [w, h], 'wallFormat': 'PNG', 'wallMode': 'RGB',
              'wallSha256': hashlib.sha256(encoded).hexdigest(),
              'changedPixels': changed, 'unchangedPixels': w*h-changed,
              'changedPixelBounds': bounds, 'allPixelsOutsideAdditionUnchanged': True,
              'additionRectangle': [x0, y0, width, height],
              'deepCracksProtected': True,
              'previewSize': [512, 512], 'previewFormat': 'JPEG',
              'previewBytes': len(preview), 'previewQuality': quality,
              'imageTool': 'built-in image_gen.imagegen; import_generated_image',
              'promptSummary': 'One worn yellow-ochre protective loop enclosing a charcoal heavy-lidded frog eye with red ochre iris. Generated pigment added to vacant ancestor stone; no hands, text or borders.',
              'reviewStatus': 'requires final visual inspection',
              'unmetVisualRequirements': []}
    (ROOT / 'gathering/wall-review-04.json').write_text(json.dumps(review, indent=2)+'\n')
    print(json.dumps(review, indent=2))


if __name__ == '__main__':
    main()
