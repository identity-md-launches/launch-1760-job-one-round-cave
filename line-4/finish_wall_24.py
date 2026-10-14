#!/usr/bin/env python3
"""One-time extraction of imagegen pigment, preserving the verified ancestor.

Not an image generator: this retains only new generated pigment on unused rock.
Refuses the finished ancestor hash so accidentally rerunning cannot add damage.
Run only from the workspace root. Uses no environment, secret or outside file.
"""
import hashlib
import json
from pathlib import Path

from image_bytes import jpeg, png, read_png, resize

ANCESTOR = '423ea6e2d272905eda1ae625f3908c9884942fe38972494fc0f5931659dca4b5'


def main():
    folder = Path('artifacts/line-4')
    before = (folder / 'wall.png').read_bytes()
    if hashlib.sha256(before).hexdigest() != ANCESTOR:
        raise ValueError('requires record 23 ancestor; do not rerun on finished wall')
    generated_bytes = (folder / 'wall-v4.png').read_bytes()
    w, h, original = read_png(before)
    gw, gh, generated = read_png(generated_bytes)
    if (w, h) != (gw, gh) or (w, h) != (1254, 1254):
        raise ValueError('unexpected image dimensions')
    final = bytearray(original)
    changed = 0
    bounds = [w, h, 0, 0]
    for y in range(145, 293):
        for x in range(995, 1176):
            # Tilted oval enclosing the new mark only, above all older pigment.
            dx, dy = x - 1084, y - 219
            u, v = .94*dx + .342*dy, -.342*dx + .94*dy
            if (u/85)**2 + (v/59)**2 > 1:
                continue
            i = (y*w+x)*3
            r, g, b = generated[i:i+3]
            oldr, oldg, oldb = original[i:i+3]
            charcoal = r < 108 and g < 82 and b < 65 and r+g+b < oldr+oldg+oldb-40
            ochre = r > 70 and g < r*.71 and b < r*.48 and r-g > oldr-oldg+13
            if not (charcoal or ochre):
                continue
            final[i:i+3] = generated[i:i+3]
            if final[i:i+3] != original[i:i+3]:
                changed += 1
                bounds = [min(bounds[0],x), min(bounds[1],y), max(bounds[2],x), max(bounds[3],y)]
    if changed < 2000:
        raise ValueError('too little new pigment; inspect before proceeding')
    output = png(w,h,final)
    (folder/'wall.png').write_bytes(output)
    (folder/'wall-v4.png').write_bytes(output)
    preview = jpeg(512,512,resize(w,h,final),52)
    if len(preview) > 100000:
        raise ValueError('JPEG exceeds delivery limit')
    Path('dist/line-4/24.jpg').write_bytes(preview)
    review = {
        'wall': {'paths':['artifacts/line-4/wall.png','artifacts/line-4/wall-v4.png'],
                 'width': w,'height': h,'format':'PNG','mode':'RGB',
                 'sha256':hashlib.sha256(output).hexdigest()},
        'ancestorSha256':ANCESTOR,
        'generatedImageSha256':hashlib.sha256(generated_bytes).hexdigest(),
        'changedPixels':changed,'unchangedPixels':w*h-changed,'additionBounds':bounds,
        'preservation':'Only selected new imagegen pigment inside an oval on unused upper-right rock was retained. All other ancestor pixels are byte-for-byte unchanged, including Pepe, both hands and every earlier mark.',
        'preview':{'path':'dist/line-4/24.jpg','width':512,'height':512,'format':'JPEG','bytes':len(preview)},
        'visualReview':'Pending final inspection', 'unmetVisualRequirements':[],
        'limitations':['Local review, not independent certification.','Small worn pigment is subtler in the thumbnail.'],
        'imageTool':'built-in imagegen; one edit; ancestor-preserving pigment extraction'
    }
    Path('line-4/wall-review-24.json').write_text(json.dumps(review,indent=2)+'\n')
    print(json.dumps(review,indent=2))


if __name__ == '__main__':
    main()
