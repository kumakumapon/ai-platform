# main branch repository ruleset

GitHub settings are repository administration, so they are not applied by a source change in this repository. Create an active repository ruleset for the `main` branch after the Repository CI workflow has run successfully on its default branch.

## Recommended configuration

1. Open **Settings → Rules → Rulesets → New branch ruleset**.
2. Name it `Protect main`, set **Enforcement status** to **Active**, and target the branch name pattern `main`.
3. Leave the bypass list empty so administrators and maintainers use the same merge gate.
4. Enable **Restrict deletions** and **Block force pushes**.
5. Require a pull request before merging. Do not require approvals (this repository is maintained by one person; CODEOWNERS/approval policy is out of scope).
6. Require the `test` status check from **Repository CI**. Require the branch to be up to date before merging so the check covers the current `main`.
7. Save the ruleset and confirm its status in the Rulesets page.

With the PR requirement active and no bypass actors, normal direct pushes to `main` are blocked. The deletion and force-push rules prevent those operations as well. Emergency work should use a PR with the same CI check; if a temporary bypass is unavoidable, an administrator should document the reason and remove the exception immediately afterward.

## Verification

After saving, verify the ruleset targets `main`, is active, has no bypass actors, and lists `test` as required. Open a small test PR and confirm the check is required before merge. Do not test by attempting an unauthorized direct push to the production branch.

## Automation boundary

The GitHub connector available for this work can read repository settings but cannot create or update rulesets. This document is the exact configuration to apply; the issue's runtime protection conditions remain pending until an administrator applies and verifies it in GitHub.
