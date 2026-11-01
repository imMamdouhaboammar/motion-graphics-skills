# OpenCV Alpha Blending and Compositing Math

Techniques for compositing multi-layer RGBA images in NumPy and OpenCV.

## Fast Alpha Blending Formula

To composite foreground array `fg` with alpha channel `alpha` over background array `bg`:

```python
import numpy as np

def composite_layers(bg, fg, alpha):
    norm_alpha = alpha.astype(float) / 255.0
    norm_alpha = np.expand_dims(norm_alpha, axis=-1)
    out = (fg.astype(float) * norm_alpha) + (bg.astype(float) * (1.0 - norm_alpha))
    return out.astype(np.uint8)
```

## Motion Blur Simulation

Accumulate subframe samples across a small time delta (e.g. 8 sub-samples per frame) with temporal weighting to achieve smooth cinematic motion blur without stepping artifacts.
