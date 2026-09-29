# main branch repository ruleset

GitHub settings are repository administration, so they are not applied by a source change in this repository. Create an active repository ruleset for the `main` branch after the Repository CI workflow has run successfully on its default branch.

## Recommended configuration

1. Download `.github/rulesets/protect-main.json` from this repository.
2. Open **Settings → Rules → Rulesets → New ruleset → Import a ruleset**, select the JSON file, review it, then create the ruleset. GitHub documents importing repository rulesets from JSON in [Managing rulesets for a repository](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/managing-rulesets-for-a-repository#importing-a-ruleset).
3. Confirm enforcement is **Active**, target is `main`, and the bypass list is empty.
4. The imported configuration requires a PR, requires the `test` status check and up-to-date branch, blocks force pushes, and prevents deletion. It does not require approvals (single maintainer; CODEOWNERS/approval policy is out of scope).
5. Save and confirm the ruleset appears on the Rulesets page.

With the PR requirement active and no bypass actors, normal direct pushes to `main` are blocked. The deletion and force-push rules prevent those operations as well. Emergency work should use a PR with the same CI check; if a temporary bypass is unavoidable, an administrator should document the reason and remove the exception immediately afterward.

## Verification

After saving, verify the ruleset targets `main`, is active, has no bypass actors, and lists `test` as required. Open a small test PR and confirm the check is required before merge. Do not test by attempting an unauthorized direct push to the production branch.

## Automation boundary

The repository contains an importable JSON configuration, but the connected GitHub operations cannot create or update repository rulesets. The issue's runtime protection conditions remain pending until a repository administrator imports the file and verifies it in GitHub.
