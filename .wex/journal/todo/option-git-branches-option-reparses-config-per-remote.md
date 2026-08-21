# branches_option re-parses raw config inside the per-remote loop

**Source**: `packages/filestate-git/src/wexample_filestate_git/option/_git/branches_option.py:85`
**Agent**: agent:performance
**Bucket**: restructure
**Severity**: perf

## Symptom
In `create_required_operation`, the `for remote in repo.remotes` loop re-iterates
`raw.items()` and re-runs the `isinstance(config, dict)` / `aliases` extraction for every
remote. That config parsing is invariant across remotes, so with R remotes and N config
entries it does R×N parsing work instead of N.

## Suggested direction
Precompute the list of `(canonical, aliases)` (post-validation, honoring `sync_remote`)
once before entering the remote loop, then only intersect against each remote's
`remote_heads` inside the loop. Marginal unless repos commonly have many remotes/configs —
benchmark before restructuring.
