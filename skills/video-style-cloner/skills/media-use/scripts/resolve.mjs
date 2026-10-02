#!/usr/bin/env node
import { spawnSync } from "node:child_process";
import { resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { resolveNpxInvocation } from "./lib/npx-sync.mjs";

// Use npm's JS CLI on Windows instead of trying to execute its .cmd shim.
// --no-install keeps this wrapper limited to an already installed HyperFrames.
export function runResolve(args, { platform = process.platform, env = process.env, opts = {} } = {}) {
  const invocation = resolveNpxInvocation(
    ["--no-install", "hyperframes", "media-use", "resolve", ...args],
    { stdio: "inherit", ...opts },
    platform,
    env,
  );
  return spawnSync(invocation.cmd, invocation.args, { ...invocation.opts, env });
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try {
    const result = runResolve(process.argv.slice(2));
    if (result.error) throw result.error;
    process.exit(result.status ?? 1);
  } catch (error) {
    console.error(`Cannot run installed HyperFrames CLI: ${error.message}. Install hyperframes and ensure npm is available.`);
    process.exit(1);
  }
}
