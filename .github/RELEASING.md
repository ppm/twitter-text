# XCFramework releases

## Initial setup

Merge the workflow and scripts into the default branch. In Settings → Actions →
General, enable Actions and “Allow GitHub Actions to create and approve pull requests”.
The workflow uses the repository's GITHUB_TOKEN; no personal token secret is needed.

Before the first release, Package.swift references build/TwitterText.xcframework
for local development. Build products are ignored by Git. The first release PR
replaces this path with the release asset URL and checksum.

## Each release

1. Open Actions → Release XCFramework → Run workflow on the default branch.
   Choose `prepare` and an unused semantic version, such as `v3.1.0-spm.1`.
   This builds iOS device, iOS Simulator and macOS frameworks, creates a draft
   release with the ZIP and Package.swift, and opens a Package.swift update PR.
2. Review and merge that PR. Its URL becomes accessible when the draft is published.
3. Run the workflow again with `publish` and the same version. It verifies the
   downloaded ZIP checksum and merged manifest, then publishes the release with
   the tag pointing at the merged commit. Source changes since the build cause
   publication to stop; prepare a new version from the updated source in that case.

The ZIP preserves framework symlinks and includes both library licenses.
The workflow selects Xcode 16.4 on macos-15; change these together when updating
build tools. Existing releases and tags are never overwritten by publication.

If preparation fails at PR creation after pushing the release branch, resolve
the reported cause and run `resume` with the same version. It verifies the existing
draft ZIP, manifest, and branch, then creates the missing PR. The draft assets and
branch are reused. An existing PR is reported instead of creating another one.

Publication permits changes to these release automation files since preparation:
`scripts/release.py`, `.github/workflows/release.yml`, and `.github/RELEASING.md`.
Other files except Package.swift must still match the build source commit.
