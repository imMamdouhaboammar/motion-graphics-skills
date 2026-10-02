import { test } from "node:test";
import assert from "node:assert/strict";
import { chmodSync, mkdirSync, mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { heygenAuthHeaders, heygenAuthMethod, heygenCredential } from "./heygen.mjs";

function withCleanHeygenEnv(fn) {
  const previousApiKey = process.env.HEYGEN_API_KEY;
  const previousHyperframesApiKey = process.env.HYPERFRAMES_API_KEY;
  const previousConfigDir = process.env.HEYGEN_CONFIG_DIR;
  try {
    delete process.env.HEYGEN_API_KEY;
    delete process.env.HYPERFRAMES_API_KEY;
    delete process.env.HEYGEN_CONFIG_DIR;
    return fn();
  } finally {
    if (previousApiKey === undefined) delete process.env.HEYGEN_API_KEY;
    else process.env.HEYGEN_API_KEY = previousApiKey;
    if (previousHyperframesApiKey === undefined) delete process.env.HYPERFRAMES_API_KEY;
    else process.env.HYPERFRAMES_API_KEY = previousHyperframesApiKey;
    if (previousConfigDir === undefined) delete process.env.HEYGEN_CONFIG_DIR;
    else process.env.HEYGEN_CONFIG_DIR = previousConfigDir;
  }
}

test("heygenAuthHeaders does not tag API-key requests as CLI traffic, but still carries the media-use tool tag", () => {
  withCleanHeygenEnv(() => {
    process.env.HEYGEN_API_KEY = "hg_test";
    // API-key requests use normal billing; the backend ignores the cli-source
    // header for them, so it's not sent. The tool-attribution header IS sent on
    // every media-use call (any auth type) so the backend can isolate media-use.
    assert.deepEqual(heygenAuthHeaders(), {
      "X-Api-Key": "hg_test",
      "X-HeyGen-Client-Source": "media-use",
    });
  });
});

test("heygenAuthHeaders tags OAuth requests as CLI traffic and with the media-use tool tag", () => {
  withCleanHeygenEnv(() => {
    const dir = mkdtempSync(join(tmpdir(), "heygen-cred-"));
    try {
      process.env.HEYGEN_CONFIG_DIR = dir;
      writeFileSync(
        join(dir, "credentials"),
        JSON.stringify({
          oauth: {
            access_token: "at_test",
            expires_at: "2099-01-01T00:00:00Z",
          },
        }),
        { mode: 0o600 },
      );
      assert.deepEqual(heygenAuthHeaders(), {
        Authorization: "Bearer at_test",
        "X-HeyGen-Source": "cli",
        "X-HeyGen-Client-Source": "media-use",
      });
    } finally {
      rmSync(dir, { recursive: true, force: true });
    }
  });
});

test("heygenAuthMethod returns api_key for an env API key, without tagging headers", () => {
  withCleanHeygenEnv(() => {
    process.env.HEYGEN_API_KEY = "hg_test";
    assert.equal(heygenAuthMethod(), "api_key");
  });
});

test("heygenAuthMethod returns oauth for a live OAuth credential", () => {
  withCleanHeygenEnv(() => {
    const dir = mkdtempSync(join(tmpdir(), "heygen-cred-"));
    try {
      process.env.HEYGEN_CONFIG_DIR = dir;
      writeFileSync(
        join(dir, "credentials"),
        JSON.stringify({
          oauth: {
            access_token: "at_test",
            expires_at: "2099-01-01T00:00:00Z",
          },
        }),
        { mode: 0o600 },
      );
      assert.equal(heygenAuthMethod(), "oauth");
    } finally {
      rmSync(dir, { recursive: true, force: true });
    }
  });
});

test("heygenAuthMethod returns null with no credential at all", () => {
  withCleanHeygenEnv(() => {
    const dir = mkdtempSync(join(tmpdir(), "heygen-cred-"));
    try {
      process.env.HEYGEN_CONFIG_DIR = dir; // no credentials file written
      assert.equal(heygenAuthMethod(), null);
    } finally {
      rmSync(dir, { recursive: true, force: true });
    }
  });
});

function withCredentialFile(fn) {
  withCleanHeygenEnv(() => {
    const dir = mkdtempSync(join(tmpdir(), "heygen-permissions-"));
    try {
      process.env.HEYGEN_CONFIG_DIR = dir;
      fn(join(dir, "credentials"));
    } finally {
      rmSync(dir, { recursive: true, force: true });
    }
  });
}

test("private plain and JSON API-key credentials remain usable", () => {
  withCredentialFile(file => {
    writeFileSync(file, "hg_fixture", { mode: 0o600 });
    assert.deepEqual(heygenCredential(), { headers: { "X-Api-Key": "hg_fixture" } });
    writeFileSync(file, JSON.stringify({ api_key: "hg_json_fixture" }));
    assert.deepEqual(heygenCredential(), { headers: { "X-Api-Key": "hg_json_fixture" } });
  });
});

test("POSIX credentials with any group or other access are rejected", { skip: process.platform === "win32" }, () => {
  withCredentialFile(file => {
    writeFileSync(file, "hg_fixture", { mode: 0o600 });
    for (const mode of [0o640, 0o602, 0o610, 0o644, 0o666]) {
      chmodSync(file, mode);
      assert.equal(heygenCredential(), null, `mode ${mode.toString(8)}`);
    }
    chmodSync(file, 0o600);
    assert.equal(heygenAuthMethod(), "api_key");
  });
});

test("credential filesystem failures and invalid JSON never throw", () => {
  withCredentialFile(file => {
    mkdirSync(file);
    assert.doesNotThrow(() => assert.equal(heygenCredential(), null));
    rmSync(file, { recursive: true });
    assert.equal(heygenCredential(), null);
    for (const raw of ["", "{broken", "{}", "{\"oauth\":null}"]) {
      writeFileSync(file, raw, { mode: 0o600 });
      assert.doesNotThrow(() => assert.equal(heygenCredential(), null));
    }
  });
});

test("environment credentials take precedence over rejected file permissions", () => {
  withCredentialFile(file => {
    writeFileSync(file, "hg_file_fixture", { mode: 0o644 });
    process.env.HEYGEN_API_KEY = "hg_env_fixture";
    assert.deepEqual(heygenCredential(), { headers: { "X-Api-Key": "hg_env_fixture" } });
  });
});
