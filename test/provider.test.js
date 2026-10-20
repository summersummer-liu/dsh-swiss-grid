import { test } from 'node:test'
import assert from 'node:assert/strict'
import { existsSync, statSync } from 'node:fs'
import { apply, inject, name, parseFrontmatter } from '../index.js'

function createContext() {
  let factory
  const ctx = { skills: { registerProvider: (fn) => { factory = fn } } }
  return { ctx, provider: () => factory?.() }
}

test('exports a skills bundle', () => {
  assert.equal(name, 'dsh-swiss-grid')
  assert.deepEqual(inject, ['skills'])
})

test('provider lists the bundled skill', async () => {
  const { ctx, provider } = createContext()
  apply(ctx)
  const p = provider()
  assert.ok(p)
  assert.equal(p.name, 'dsh-swiss-grid')
  const listed = await p.list({})
  assert.equal(listed.length, 1)
  const skill = listed[0]
  assert.equal(skill.name, 'swiss-grid-design')
  assert.ok(skill.description.includes('grid'))
  assert.equal(skill.source, 'bundled')
  assert.equal(skill.provider, 'dsh-swiss-grid')
  assert.equal(skill.resourceBase.kind, 'directory')
  assert.ok(existsSync(skill.resourceBase.path))
  assert.ok(statSync(skill.resourceBase.path).isDirectory())
  assert.equal(skill.invocation.modelInvocable, true)
  assert.equal(skill.invocation.userInvocable, true)
})

test('provider returns the full skill definition', async () => {
  const { ctx, provider } = createContext()
  apply(ctx)
  const p = provider()
  const definition = await p.get({ name: 'swiss-grid-design' }, {})
  assert.ok(definition)
  assert.equal(definition.name, 'swiss-grid-design')
  assert.ok(definition.content.startsWith('# Swiss Grid Design'))
  assert.ok(definition.path.endsWith('SKILL.md'))
  assert.equal(definition.metadata?.version, '1.1')
})

test('unknown skill names resolve to undefined', async () => {
  const { ctx, provider } = createContext()
  apply(ctx)
  const p = provider()
  assert.equal(await p.get({ name: 'does-not-exist' }, {}), undefined)
})

test('frontmatter parser handles nested metadata and rejects malformed files', () => {
  const parsed = parseFrontmatter('---\nname: demo\ndescription: "a demo"\nmetadata:\n  version: "1.0"\n---\n\n# Demo\n')
  assert.equal(parsed.data.name, 'demo')
  assert.equal(parsed.data.description, 'a demo')
  assert.equal(parsed.data.metadata.version, '1.0')
  assert.equal(parsed.body.trim(), '# Demo')
  assert.throws(() => parseFrontmatter('no frontmatter here'), /must start with/)
  assert.throws(() => parseFrontmatter('---\nname: x\n'), /unterminated/)
})
