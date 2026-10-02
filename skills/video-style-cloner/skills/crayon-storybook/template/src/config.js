// config.js: project settings.
//   duration: the video's length in seconds.
//   bpm:      the rhythm idles, bounces and pulse() follow. With music, set it to the song's tempo and offset to the
//             time in seconds of its first downbeat.
//   fps:      output frame rate (render.mjs reads --fps; 24 is the storybook default).
//   boil:     linework boil rate in drawings per second (default 8: slow, re-drawn-by-hand).
//   toothBoil: false keeps the paper tooth fixed on screen (default: it shifts with each boil drawing).
const PROJECT = { duration: 10, bpm: 96, offset: 0, fps: 24 };
