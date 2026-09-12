# Releasing

For whoever maintains `Pantheosis/TAE`. Users never need this page; builders have
`BUILD_NOTES.md`.

## Where things live

- **Source and releases:** this repository. A release's binaries sit beside the exact source
  they were built from (the tag), which the AGPL requires and which lets anyone check a binary
  against its code. `TAE-Releases` is retired (a pointer README; archived).
- **The texts** are not in the repository and never will be: they are copyrighted translations,
  worked from privately. Nothing in a release or a workflow may copy them.

## The routine

Every change reaches `main` by pull request; `main` has a ruleset (no force-push, no deletion,
PR required, the `pytest` check required, no bypass). Merge when the check is green.

1. **Test a build without releasing.** Actions → *Build Desktop App* → *Run workflow* → `main`.
   About 25 minutes later the run page has two artifacts (`TraditionalAstrologyEngine-Windows`,
   `-macOS`), kept three days, no release made. GitHub wraps an artifact in its own zip on
   download, so the Windows one unzips to `TraditionalAstrologyEngine-windows.zip`; unzip
   again. The build is byte-for-byte what the tag would produce from the same commit.
2. **Release.** On `main`, at the commit you tested:

   ```bash
   git tag -a v1.2.0 -m "Traditional Astrology Engine v1.2.0"
   git push origin v1.2.0
   ```

   The workflow builds both platforms and creates the GitHub release `v1.2.0` with the two zips
   attached and auto-generated notes; edit the notes on the release page. A push to `main`
   builds nothing — only a `v*` tag or a manual run does.
3. **Version numbers.** v0.8-beta (this repo) and v1.0.0 / v1.1.0 (the retired repo, deleted)
   are spent even where deleted: people downloaded them. Next is v1.2.0; a minor bump for new
   rules and wording, a major one when what the app computes on every chart changes.
4. **Undoing a release.** `gh release delete v1.2.0 --yes && git push origin :refs/tags/v1.2.0`
   removes the release, its assets and the tag; the source commit stays.

## The suite in CI

`tests.yml` runs the full suite on every PR and push to `main` (about 25 minutes on the 2-core
runner; the stuck-job guard is 45). Seven tests skip in CI because they read the private corpus;
they run locally. A run that ends *cancelled* rather than *failed* hit the guard, not a test.
