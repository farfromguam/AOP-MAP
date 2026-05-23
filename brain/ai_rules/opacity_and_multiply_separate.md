# Opacity and multiply are separate

TL;DR: In the viewer, opacity and multiply (paper-white keying) are independent attributes. Substrate state can drive multiply; it must not auto-adjust the opacity slider.

#ai_rules #viewer #sfwda #compositing

-----

Two different attributes, two different jobs:

- **Opacity** is a uniform alpha blend the user tunes for readability.
- **Multiply** is the canvas alpha-key that drops paper-white to transparent — a structural compositing decision tied to whether there is a substrate worth seeing through to.

Coupling them makes basemap toggles silently override the user's opacity choice. That is surprising and wrong.

In `website/index.html`, when satellite/hillshade toggles change, only call `rebakeTiles()` if `sfwdaMultiplyMode` flipped. Never write to `sfwdaOpacity.value` or call `setSfwdaOpacity()` from a basemap-toggle handler. The opacity slider's `input` listener is the only thing that should set opacity.

If the user says "default per substrate," ask whether they mean the multiply default or the opacity default — they are not the same lever.
