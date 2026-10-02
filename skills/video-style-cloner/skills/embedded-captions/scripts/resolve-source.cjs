#!/usr/bin/env node
// Resolve once before prepare's concurrent workers. Preserve an explicit source.mp4;
// otherwise adopt the largest input clip (stable filename order breaks size ties).
const fs = require('fs');
const path = require('path');

function resolveSource(project) {
  const source = path.join(project, 'source.mp4');
  if (fs.existsSync(source)) return source;
  if (fs.lstatSync(source, { throwIfNoEntry: false })) {
    throw new Error('source.mp4 exists but its target is missing; repair it before preparing');
  }
  const candidates = fs.readdirSync(project)
    .filter(name => /\.(mp4|mov|webm|mkv|m4v)$/i.test(name) &&
      !/^(_|final(?:\.|$)|bg_plus_caps(?:\.|$)|fg_caps(?:\.|$)|audio(?:\.|$)|rail(?:\.|$)|index(?:\.|$))/i.test(name))
    .map(name => ({ name, stat: fs.statSync(path.join(project, name)) }))
    .filter(candidate => candidate.stat.isFile())
    .sort((a, b) => b.stat.size - a.stat.size || (a.name < b.name ? -1 : a.name > b.name ? 1 : 0));
  if (!candidates.length) throw new Error('no input video found; provide source.mp4');
  const selected = candidates[0].name;
  try {
    fs.symlinkSync(selected, source);
  } catch (error) {
    // Git Bash/Windows may not allow symlinks. Never overwrite a source created by
    // another invocation: exclusive copy fails cleanly instead of following its link.
    if (error.code === 'EEXIST') throw error;
    fs.copyFileSync(path.join(project, selected), source, fs.constants.COPYFILE_EXCL);
  }
  console.log(`[prepare] resolved source.mp4 -> ${selected}`);
  return source;
}

if (require.main === module) {
  if (!process.argv[2]) {
    console.error('usage: resolve-source.cjs <project-dir>');
    process.exit(1);
  }
  try {
    resolveSource(path.resolve(process.argv[2]));
  } catch (error) {
    console.error(`[prepare] ${error.message}`);
    process.exit(1);
  }
}
module.exports = { resolveSource };
