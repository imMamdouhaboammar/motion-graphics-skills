# QA: متلبس بالشطارة

Export verified: H.264 High, 1920 × 1080, 30fps, 3369 frames, 112.300s, BT.709, stereo AAC 48kHz. Audio and video durations match. Full frame decode completed. No one-frame flashes detected. Luma jumps at 47.000s and 69.300s correspond to the night/day scene cuts.

## Dialogue completeness and synchronization

Original WAV: 5,359,073 samples, 111.647354s, SHA256 e5849b165bcab62486d80a4ecc45697c925040553269d795f80769b5ccac336a. The source is copied byte-identically and played from zero at its full length. No replacement, reordering, narration synthesis or truncation. AAC final mix is lossy, so output samples are not byte-identical. Source/output correlation was checked in all 112 one-second voiced windows: minimum 0.9516, median 0.9968, with no timing offset. Decoded mix peak 0.7537, below digital clipping. Closing windows 108–111s correlate 0.9976, 0.9976, 0.9891, 0.9994. Music and SFX are separate original tracks and the original narration gain is 1 in the composition.

## Acting, visual consistency and ending

Twenty sampled frames from the actual full export, plus sequential frames from all four motion proofs, were inspected. The teal professional retains the same face, hair, outfit, and proportions. The lavender client remains distinct. Raised shoulder/forearm rigs, facial path changes, eyelids, logo strokes, camera pushes, laptop closing/reopening, calendar collapse, scale tilt, and the coin cart are authored SVG/GSAP animation. These are cutout rigs with held poses, not frame-by-frame hand-drawn animation. Mouth poses are expressive, not certified phoneme lip-sync.

The arrest hands and finger direction, night frown, laptop reach, scale rope connections and camera scale were corrected before this export. Final gag uses two complete coins and a half coin, arriving during the exact original closing phrase. Fade begins at 111.66s, after the full WAV has played. No on-screen Arabic captions were used.

## Machine warnings and limits

HyperFrames check passes with zero errors. Seventeen architecture warnings concern one file with 16 nested SVG scenes. Three pivot-drift warnings refer to limbs deliberately rotating at shoulders, rather than spinning at their geometric center. The scene11 camera overflow clips lower furniture during the push. Freeze detection reports many held poses in the sparse flat art; some stretches intentionally have only blinks or facial movement. Several transitions are direct cuts rather than continuous shape handoffs. The last scene is quieter and more limited in body movement.

Review is based on decoded frame sequences, source animation inspection, and quantitative audio analysis. Full normal-speed sound-on human playback and a word-by-word listening certification were not available in this environment. Therefore the strict video-review-loop human playback gate remains unfulfilled. A clean technical export is not a claim of perfect creative quality or complete human signoff. The transcript timing is ASR phrase anchored and corrected against the supplied script, not manually certified to each spoken word.

## Music and assets

Character and environment SVGs were drawn originally for this film. Music and sound design are deterministic procedural compositions created for the project; no stock recordings, copied characters, or reference logos are used. The supplied narration remains the user's asset. GSAP and HyperFrames retain their respective third-party licenses.
