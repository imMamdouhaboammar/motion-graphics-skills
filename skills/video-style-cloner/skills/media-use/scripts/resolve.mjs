#!/usr/bin/env node
import { spawnSync } from "node:child_process";

const result = spawnSync("hyperframes", ["media-use", "resolve", ...process.argv.slice(2)], {
  stdio: "inherit",
});
if (result.error) console.error(`Cannot run installed HyperFrames CLI: ${result.error.message}. Install hyperframes and ensure it is on PATH.`);
process.exit(result.status ?? 1);
