# Stone Sieve: local image review

Built-in image generation edited the restored record 23 wall. The public
ancestor was fetched before the final workspace-only security instruction,
using a specific User-Agent, and its bytes matched the record's SHA-256:
`99ec2af1433b29ad0dbf0558e1d40e63fd3c38399d4a57c103ada7ce31dd26e8`.
No network read was needed after that instruction.

Final generation prompt:

> Use case precise-object-edit. Edit supplied original cave wall, preserving all
> ancestor marks exactly. Add a SMALL FLAT TWO-DIMENSIONAL PREHISTORIC CAVE
> PAINTING of a sieve on vacant stone BELOW the large ancestor frog. Bounds
> x630..970 y820..970 of 1254 square. The sieve is only a crude irregular
> charcoal oval with a few crosshatched burnt-stick strokes inside, outlined
> and partly rubbed away, with three flat red ochre pebble-shaped pigment daubs
> resting within its oval and a broken ochre daub beside it. This is a flat
> drawing on stone, NOT a real basket or real stones: NO VOLUME, NO DEPTH,
> NO SHADOW, NO highlights, no rendered weave. Emulate the ancestor's worn flat
> earth pigment showing stone texture. Preserve existing three Pepe paintings,
> pebbles, rock cracks light water framing. No new hands. No text, numbers letters
> signature logo frame watermark prohibited symbols. Every existing mark stays
> identical. Final 1254x1254 PNG.

The first generation looked like a physical basket and was replaced by the
flat-pigment version after inspection. The finished image uses only the latter.
The tool's returned image bytes were saved directly within the permitted folder;
no generated-file cache outside the workspace was read.

A local ffmpeg composition selected dark charcoal and red ochre pixels from
rectangle `(565,805)` through `(875,965)`, using the generated color predicate
`(R<95 and G<75 and B<50) or (R>1.65*G and G<80 and B<50)`. Selected pixels were
composited onto the original wall; all other pixels came from the ancestor.
The three ancestor figures and their marks are outside this rectangle. The
output was RGB PNG with the original dimensions; identical final bytes went
to `artifacts/line-2/wall.png` and `artifacts/line-2/wall-v4.png`.
The temporary generated variant was overwritten at that same declared path.

This preserves the ancestor pixels outside the region by construction. No
independent ancestor-versus-final pixel count was retained, and none is claimed.
Inside the region the selected pigment covers small areas of previously vacant
stone, while its surrounding rock remains visible. It is an additive painting,
not an erasure or redraw of existing marks.

Reviewed the final full wall and decoded preview. Three inherited Pepe figures
retain their wide mouths and heavy-lidded eyes. The added sieve is worn, flat
charcoal/ochre pigment. The square cave, warm rough rock, cracks, light and water
remain. No distinct hands, handprints or stencils are depicted, so no visible
finger groups require a digit count. No letters, numbers, captions, logos,
signatures, watermarks, borders, frames, real people or prohibited symbols were
observed. No known unmet visual requirements. This is a local visual review,
not an independent aesthetic assessment.

Final PNG: **1254 × 1254**, RGB, **3,947,715 bytes**.
Preview: `dist/line-2/24.jpg`, **512 × 512 JPEG**, **70,896 bytes**.
Record: `dist/line-2/24.json`; its URL is the final PNG's lowercase SHA-256.
`validation.json` records structural decoding and local checks.
