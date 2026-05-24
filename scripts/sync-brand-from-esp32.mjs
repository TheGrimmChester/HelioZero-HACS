#!/usr/bin/env node
/**
 * Copy canonical brand SVGs from HelioZero-ESP32 (sibling repo).
 * Edit sources only under HelioZero-ESP32/assets/brand/.
 */
import { copyFileSync, existsSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const esp32Brand = join(root, "..", "HelioZero-ESP32", "assets", "brand");
const outDir = join(root, "assets", "brand");

const files = [
  "helio-zero-favicon.svg",
  "helio-zero-logo-light.svg",
  "helio-zero-logo-dark.svg",
];

if (!existsSync(esp32Brand)) {
  console.error(`sync-brand-from-esp32: missing ${esp32Brand}`);
  process.exit(1);
}

mkdirSync(outDir, { recursive: true });
for (const name of files) {
  const src = join(esp32Brand, name);
  if (!existsSync(src)) {
    console.error(`sync-brand-from-esp32: missing ${src}`);
    process.exit(1);
  }
  copyFileSync(src, join(outDir, name));
  console.log(`sync-brand-from-esp32: ${name}`);
}
