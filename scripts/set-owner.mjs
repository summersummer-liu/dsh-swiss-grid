#!/usr/bin/env node
/**
 * Replace the OWNER placeholder in package.json and the READMEs with a GitHub
 * account/org name, and point repository/homepage/bugs at the right repo.
 *
 * Usage: node scripts/set-owner.mjs <github-owner> [repo-name]
 */
import { readFileSync, writeFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { dirname, join } from 'node:path'

const here = dirname(fileURLToPath(import.meta.url))
const root = join(here, '..')

const owner = process.argv[2]
const repo = process.argv[3] ?? 'dsh-swiss-grid'
if (!owner || !/^[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})$/.test(owner)) {
  console.error('Usage: node scripts/set-owner.mjs <github-owner> [repo-name]')
  process.exit(1)
}
if (!/^[a-z0-9][a-z0-9._-]*$/.test(repo)) {
  console.error('Invalid repo name:', repo)
  process.exit(1)
}

const pkgPath = join(root, 'package.json')
const pkg = JSON.parse(readFileSync(pkgPath, 'utf8'))
pkg.repository = { type: 'git', url: `https://github.com/${owner}/${repo}.git` }
pkg.homepage = `https://github.com/${owner}/${repo}`
pkg.bugs = { url: `https://github.com/${owner}/${repo}/issues` }
writeFileSync(pkgPath, `${JSON.stringify(pkg, null, 2)}\n`)

for (const file of ['README.md', 'README.zh-CN.md', 'PUBLISHING.md']) {
  const path = join(root, file)
  let text = readFileSync(path, 'utf8')
  text = text.replaceAll('OWNER/dsh-swiss-grid', `${owner}/${repo}`)
  writeFileSync(path, text)
}

console.log(`owner -> ${owner}`)
console.log(`repo  -> ${owner}/${repo}`)
console.log('next: git init -b main && git add -A && git commit -m "feat: dsh-swiss-grid 1.1.0"')
