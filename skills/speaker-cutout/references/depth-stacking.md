# Depth Stacking and Speaker Cutout Rules

These principles governPresenter segmentation, layer stacking, and background replacement.

## 1. The four visual layers

Proper depth composition always maintains this strict rendering order from back to front:

1. **Layer 0 (Background):** The base plate, solid brand background, or 3D world.
2. **Layer 1 (Behind-speaker Graphics):** Titles, animated charts, glowing shapes, or diagrams.
3. **Layer 2 (Presenter Cutout):** The keyed or segmented speaker with alpha channel.
4. **Layer 3 (Foreground UI):** Captions, progress bars, and channel watermarks.

Because captions sit in Layer 3, they are never obscured by the presenter. Because motion graphics sit in Layer 1, the presenter naturally overlaps them without artificial clipping.

## 2. Transition order prevents double vision

When transitioning the speaker from full screen into a picture-in-picture card:
- Never move the speaker and change the background at the exact same frame if using an empty room plate.
- First swap the camera background to the new backdrop plate.
- Then shrink and slide the speaker cutout to the target corner or side.
- This two-step sequence ensures viewers never perceive two copies of the speaker or room simultaneously.

## 3. Empty room plate best practices

- Ask the speaker for a clean 5-second empty-room video recorded with the camera on a tripod from the exact same position.
- If an empty room shot exists, the real room remains behind the speaker when shrinking to PiP.
- If no empty room shot exists, replace the background entirely with a brand color gradient or blurred backdrop.

## 4. Edge feathering and lighting match

- Raw segmentation masks often have harsh 1px borders. Apply a 2px to 4px Gaussian blur to the alpha matte.
- If the new background is substantially darker than the original room, tint the edge rim slightly to prevent bright halo fringing.
