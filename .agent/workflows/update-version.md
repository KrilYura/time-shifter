---
description: How to update the integration version
---

# Update Integration Version

Use this workflow whenever you make changes to the integration that should result in a new version. There is no version script — the agent (or human) updates the version files directly.

## Steps

1. **Make your code changes**
   - Edit files in `custom_components/time_shifter/`
   - Test your changes

2. **Bump the version** (follow [Semantic Versioning](https://semver.org/))
   - **Patch** (0.1.0 → 0.1.1): bug fixes
   - **Minor** (0.1.0 → 0.2.0): new features, backwards compatible
   - **Major** (0.1.0 → 1.0.0): breaking changes

   Update all of these to the same version string:
   - `.version` — single source of truth (one line, e.g. `0.2.0`)
   - `custom_components/time_shifter/manifest.json` — `"version"` field
   - `custom_components/time_shifter/const.py` — `VERSION` constant
   - `README.md` — `**Version:** X.Y.Z` at the top

3. **Update the changelog**
   - Edit `VERSION.md`
   - Add your changes under a new version section
   - Follow the existing Keep a Changelog format

4. **Verify**
   - Confirm `.version`, `manifest.json`, `const.py`, and `README.md` all match
   - Review the changelog entry

5. **Commit, tag, push, and release** (when the user asks)

   ```bash
   git add .
   git commit -m "Release version X.Y.Z"
   git tag -a vX.Y.Z -m "Release version X.Y.Z"
   git push && git push --tags
   ```

   Then create a **GitHub Release** for tag `vX.Y.Z` (required for HACS to show a proper semver instead of a commit hash):

   ```bash
   # Preferred when gh is available
   gh release create vX.Y.Z \
     --repo KrilYura/time-shifter \
     --title "X.Y.Z" \
     --notes-file - <<'EOF'
   ## What's Changed
   - Summarize from VERSION.md
   EOF

   # Or via GitHub API (when authenticated)
   curl -X POST \
     -H "Accept: application/vnd.github+json" \
     -H "Authorization: Bearer $GITHUB_TOKEN" \
     https://api.github.com/repos/KrilYura/time-shifter/releases \
     -d '{"tag_name":"vX.Y.Z","name":"X.Y.Z","body":"...","draft":false,"prerelease":false}'
   ```

   Manual alternative: GitHub → **Releases** → **Draft a new release** → choose tag `vX.Y.Z` → paste changelog → **Publish release**.

### Why tags + releases matter

HACS shows a commit hash (e.g. `9914b91`) when the repo has no GitHub Releases. Always:

1. Push annotated tag `vX.Y.Z`
2. Publish a GitHub Release from that tag

After publishing, refresh/redownload in HACS so it picks up `vX.Y.Z`.
