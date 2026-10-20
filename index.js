/**
 * dsh-swiss-grid — DSH plugin bundle.
 *
 * Registers the bundled `skills/swiss-grid-design/SKILL.md` on `ctx.skills`,
 * so a DeepSeek Harness instance gets the Swiss-grid layout skill simply by
 * adding this package to a profile.
 *
 * Zero runtime dependencies. The provider reads the packaged SKILL.md files
 * on demand, which keeps the bundle compatible with DSH's skill hot-reload.
 *
 * @module dsh-swiss-grid
 */
import { readdir, readFile } from 'node:fs/promises'
import { join } from 'node:path'
import { fileURLToPath } from 'node:url'

const PROVIDER_NAME = 'dsh-swiss-grid'
const SKILLS_ROOT = fileURLToPath(new URL('./skills/', import.meta.url))
const SKILL_NAME = /^[a-z0-9]+(?:-[a-z0-9]+)*$/
// Bundled plugins sit above user filesystem skills (diagram-design is rank 400).
const BUNDLED_SKILL_RANK = 550

export const name = PROVIDER_NAME
export const inject = ['skills']

/**
 * Register the bundled skill provider.
 * @param {{ skills: { registerProvider: (factory: Function) => void } }} ctx
 */
export function apply(ctx) {
  ctx.skills.registerProvider(() => ({
    name: PROVIDER_NAME,
    async list(options) {
      options?.signal?.throwIfAborted()
      const skills = await loadSkills()
      options?.signal?.throwIfAborted()
      return skills.map(toCandidate)
    },
    async get(candidate, options) {
      options?.signal?.throwIfAborted()
      const skills = await loadSkills()
      const skill = skills.find((entry) => entry.name === candidate.name)
      return skill === undefined ? undefined : toDefinition(skill)
    },
  }))
}

async function loadSkills() {
  const entries = await readdir(SKILLS_ROOT, { withFileTypes: true })
  const skills = []
  for (const entry of entries) {
    if (!entry.isDirectory() && !entry.isSymbolicLink()) continue
    const directory = join(SKILLS_ROOT, entry.name)
    const skillFile = join(directory, 'SKILL.md')
    let raw
    try {
      raw = await readFile(skillFile, 'utf8')
    } catch {
      continue // no SKILL.md in this directory — ignore it
    }
    skills.push(parseSkill(raw, directory, skillFile))
  }
  return skills.sort((left, right) => left.name.localeCompare(right.name))
}

function parseSkill(raw, directory, skillFile) {
  const { data, body } = parseFrontmatter(raw)
  const skillName = typeof data.name === 'string' ? data.name.trim() : undefined
  const description = typeof data.description === 'string' ? data.description.trim() : undefined
  if (!skillName || !description) {
    throw new Error(`${PROVIDER_NAME}: ${skillFile} requires name and description in frontmatter`)
  }
  if (!SKILL_NAME.test(skillName)) {
    throw new Error(`${PROVIDER_NAME}: invalid skill name "${skillName}"`)
  }
  const metadata = typeof data.metadata === 'object' && data.metadata !== null && !Array.isArray(data.metadata)
    ? data.metadata
    : undefined
  return {
    name: skillName,
    description,
    ...(metadata !== undefined ? { metadata } : {}),
    invocation: {
      modelInvocable: data['disable-model-invocation'] !== true,
      userInvocable: data['user-invocable'] !== false,
    },
    provider: PROVIDER_NAME,
    source: 'bundled',
    resourceBase: { kind: 'directory', path: directory },
    rank: BUNDLED_SKILL_RANK,
    locator: skillFile,
    path: skillFile,
    content: body.trim(),
  }
}

/**
 * Parse the small YAML frontmatter used by SKILL.md files.
 * Supports top-level scalars and one level of nested key/value maps.
 *
 * @param {string} raw
 * @returns {{ data: Record<string, any>, body: string }}
 */
export function parseFrontmatter(raw) {
  const lines = raw.replace(/^\uFEFF/, '').split(/\r?\n/)
  if (lines[0].trim() !== '---') {
    throw new Error(`${PROVIDER_NAME}: SKILL.md must start with --- frontmatter`)
  }
  let close = -1
  for (let index = 1; index < lines.length; index += 1) {
    if (lines[index].trim() === '---') {
      close = index
      break
    }
  }
  if (close < 0) {
    throw new Error(`${PROVIDER_NAME}: unterminated SKILL.md frontmatter`)
  }
  const data = {}
  let current = null
  for (const line of lines.slice(1, close)) {
    if (line.trim() === '' || line.trimStart().startsWith('#')) continue
    const match = /^(\s*)([A-Za-z0-9_-]+):\s*(.*)$/.exec(line)
    if (!match) continue
    const [, indent, key, rawValue] = match
    const value = rawValue.trim()
    if (indent.length === 0) {
      if (value === '') {
        data[key] = {}
        current = key
      } else {
        data[key] = unquote(value)
        current = null
      }
    } else if (current !== null && typeof data[current] === 'object') {
      data[current][key] = unquote(value)
    }
  }
  return { data, body: lines.slice(close + 1).join('\n') }
}

function unquote(value) {
  if (value.length >= 2) {
    const first = value[0]
    const last = value[value.length - 1]
    if ((first === '"' && last === '"') || (first === "'" && last === "'")) {
      return value.slice(1, -1)
    }
  }
  return value
}

function toCandidate(skill) {
  return {
    name: skill.name,
    description: skill.description,
    ...(skill.metadata !== undefined ? { metadata: skill.metadata } : {}),
    invocation: skill.invocation,
    provider: skill.provider,
    source: skill.source,
    resourceBase: skill.resourceBase,
    rank: skill.rank,
    locator: skill.locator,
    path: skill.path,
  }
}

function toDefinition(skill) {
  return {
    name: skill.name,
    description: skill.description,
    ...(skill.metadata !== undefined ? { metadata: skill.metadata } : {}),
    invocation: skill.invocation,
    provider: skill.provider,
    source: skill.source,
    resourceBase: skill.resourceBase,
    path: skill.path,
    content: skill.content,
  }
}
