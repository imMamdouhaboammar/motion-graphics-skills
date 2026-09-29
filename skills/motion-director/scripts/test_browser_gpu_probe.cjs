#!/usr/bin/env node
'use strict';

const assert = require('node:assert/strict');
const path = require('node:path');

const probe = require(path.join(__dirname, 'browser_gpu_probe.cjs'));

assert.equal(probe.classifyRenderer('ANGLE (Google, Vulkan 1.3.0 (SwiftShader Device))').hardware, false);
assert.equal(probe.classifyRenderer('llvmpipe (LLVM 18.1.8, 256 bits)').hardware, false);
assert.equal(probe.classifyRenderer('ANGLE (NVIDIA, NVIDIA RTX 4090 Direct3D11)').hardware, true);
assert.equal(probe.classifyRenderer('Apple M4').hardware, true);
assert.equal(probe.classifyRenderer('ANGLE (Intel, Intel(R) Iris(R) Xe Graphics)').hardware, true);
assert.equal(probe.classifyRenderer('WebKit WebGL').hardware, false);
assert.equal(probe.classifyRenderer('ANGLE').hardware, false);
assert.equal(probe.classifyRenderer('Microsoft Basic Render Driver').hardware, false);
assert.equal(probe.classifyRenderer('').hardware, false);

assert.ok(probe.browserArgs('Darwin').includes('--use-angle=metal'));
assert.ok(probe.browserArgs('Windows').includes('--use-angle=d3d11'));
assert.ok(probe.browserArgs('Linux').includes('--use-gl=angle'));

console.log('browser GPU probe contract passed');
