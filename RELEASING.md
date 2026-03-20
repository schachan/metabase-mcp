# Releasing `metabase-mcp-plus`

Releases are automated with [`.github/workflows/publish.yml`](.github/workflows/publish.yml).

## One-time setup

### 1. PyPI trusted publisher (OIDC)

1. Log in at [pypi.org](https://pypi.org).
2. Open **[Account settings → Publishing](https://pypi.org/manage/account/publishing/)**.
3. Add a **pending publisher**:
   - **PyPI project name:** `metabase-mcp-plus` (create the project name here if the package is new).
   - **Owner:** `schachan`
   - **Repository:** `metabase-mcp`
   - **Workflow name:** `publish.yml`
   - **Environment name:** `pypi`

No long-lived PyPI token is stored in GitHub.

### 2. GitHub Environment `pypi`

1. In the repo: **Settings → Environments → New environment** → name: **`pypi`**.
2. Optional: enable **Required reviewers** so publishes need approval before PyPI upload.

## Cut a release

**Important:** When you publish a release, Actions checks out **the commit the tag points to** — not necessarily the latest `main`. The workflow file, `pyproject.toml`, and all code at **that SHA** are what run. Always create the tag on the commit that already has your version bump **and** any CI fixes.

1. **Bump** `[project].version` in `pyproject.toml` (e.g. `1.0.1`).
2. Commit **everything** that must pass CI (including Ruff-clean code and workflow updates) and **push to `main`**.
3. **Create the tag on that same commit** (e.g. in GitHub UI: choose the latest `main` commit when creating the release tag, or locally: `git tag v1.0.1` after pulling `main`, then `git push origin v1.0.1`).
4. **Create a GitHub Release** whose **tag** matches that version with a `v` prefix:
   - Example: version `1.0.1` → tag **`v1.0.1`**.
5. **Publish** the release (not a draft).

The workflow will:

- Lint and test
- Fail if the tag (without `v`) does not equal `pyproject.toml` version
- Build wheel + sdist
- Attach `dist/*` to the GitHub Release
- Publish to PyPI via trusted publishing

After success, users can run:

```bash
uvx metabase-mcp-plus
```

## Troubleshooting

| Issue | What to check |
|--------|----------------|
| Lint fails but `main` is green | The **tag** likely points at an **older commit**. Re-run won’t fix it: move the tag to a commit that passes CI, or release **`v1.0.2`** from current `main`. |
| Workflow still shows `checkout@v4` | Same as above — the run used an old tree; merge/push fixes, then tag a **new** commit. |
| “Version mismatch” | Tag `vX.Y.Z` must match `[project].version = "X.Y.Z"` in `pyproject.toml` **on the tagged commit**. |
| PyPI rejects OIDC | Trusted publisher owner/repo/workflow/environment must match exactly. |
| Workflow not listed | Push `publish.yml` to default branch; PyPI reads workflow from GitHub API. |

### Fix a bad release tag (example: `v1.0.1` pointed at the wrong commit)

1. Push all fixes to `main` and confirm the **CI** workflow is green on `main`.
2. On GitHub: **delete the Release** for `v1.0.1` (optional but avoids confusion).
3. Delete the remote tag, then re-tag the **current** `main` (only if PyPI does not already have `1.0.1`; otherwise bump to `1.0.2` instead):

   ```bash
   git checkout main && git pull
   git tag -d v1.0.1
   git push origin :refs/tags/v1.0.1
   git tag v1.0.1
   git push origin v1.0.1
   ```

4. Create and **publish** the GitHub Release again for `v1.0.1`.

If **`1.0.1` is already on PyPI**, do **not** re-tag the same version — bump `pyproject.toml` to **`1.0.2`**, push, then release **`v1.0.2`**.
