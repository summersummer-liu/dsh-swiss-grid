# Publishing dsh-swiss-grid

The repository is prepared locally with git history. Two things are still needed from the
publisher: a GitHub account/repo name, and authentication (this environment has no `gh` login
and no stored git credentials, so the push itself cannot be done unattended).

## 0. Pre-flight

```sh
node --test          # 5 tests: provider, SKILL.md parsing, definition shape
npm pack --dry-run   # inspect the package contents (no proprietary PDFs/fonts)
```

## 1. Set the owner

```sh
node scripts/set-owner.mjs <github-user-or-org> [repo-name]
```

This rewrites `repository`, `homepage`, `bugs` in `package.json` and the `summersummer-liu/dsh-swiss-grid`
links in both READMEs and this file. Default repo name: `dsh-swiss-grid`.

## 2. Create the GitHub repository

Option A — web UI: create an empty public repo `dsh-swiss-grid` (no README, no .gitignore).

Option B — GitHub CLI, if installed and logged in:

```sh
gh repo create <owner>/dsh-swiss-grid --public --source=. --remote=origin --push
```

Then skip step 3 and 4 (the command already pushed).

## 3. Commit

```sh
git init -b main
git add -A
git commit -m "feat: dsh-swiss-grid 1.1.0 — Swiss grid design plugin for DeepSeek Harness"
```

## 4. Push

```sh
git remote add origin https://github.com/<owner>/dsh-swiss-grid.git
git push -u origin main
```

Authentication: use a personal access token with `repo` scope as the password for HTTPS
(`git push https://<token>@github.com/<owner>/dsh-swiss-grid.git main`) or configure SSH.
Never commit tokens; do not put them in the remote URL stored in `.git/config`.

## 5. Optional: publish to npm

```sh
npm login
npm publish --access public
```

The package is zero-dependency and publishes only `index.js`, `cordis.patch.yml`, `skills/`,
`scripts/`, READMEs, CHANGELOG, LICENSE and NOTICE (`files` field).

## 6. Install into DSH

From GitHub:

```sh
dsh plugin --profile desktop add github:<owner>/dsh-swiss-grid
```

From npm:

```sh
dsh plugin add dsh-swiss-grid
```

Restart `dsh web`/the desktop app once, then check the skill catalog for
**`swiss-grid-design`** and optionally run a smoke test:

```sh
dsh --print-skills | findstr swiss-grid   # if your CLI supports listing
```

or simply start a session and ask for a poster — the catalog entry is the proof.

## 7. Optional: add to the DSH plugin market

The community market (dshmarket.com / awesome-dsh-plugin) accepts entries from a curated
registry; a normal GitHub repo plus npm publication is enough for direct installation. If you
want a market listing, open an issue in the registry with the repo URL, description, screenshots
and the `dsh` compatibility field from `package.json`.
