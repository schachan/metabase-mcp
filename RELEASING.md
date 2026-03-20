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

1. **Bump** `[project].version` in `pyproject.toml` (e.g. `1.0.1`).
2. Commit and push to `main`.
3. **Create a GitHub Release** whose **tag** matches that version with a `v` prefix:
   - Example: version `1.0.1` → tag **`v1.0.1`**.
4. **Publish** the release (not a draft).

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
| “Version mismatch” | Tag `vX.Y.Z` must match `[project].version = "X.Y.Z"` in `pyproject.toml`. |
| PyPI rejects OIDC | Trusted publisher owner/repo/workflow/environment must match exactly. |
| Workflow not listed | Push `publish.yml` to default branch; PyPI reads workflow from GitHub API. |
