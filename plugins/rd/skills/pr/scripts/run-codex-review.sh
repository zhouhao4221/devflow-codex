#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "usage: run-codex-review.sh --repo <path> --base-ref <ref> --base-sha <sha> --head-sha <sha>" >&2
  exit 64
}

repo_root=""
base_ref=""
base_sha=""
head_sha=""

while [ "$#" -gt 0 ]; do
  case "$1" in
    --repo)
      [ "$#" -ge 2 ] || usage
      repo_root="$2"
      shift 2
      ;;
    --base-ref)
      [ "$#" -ge 2 ] || usage
      base_ref="$2"
      shift 2
      ;;
    --base-sha)
      [ "$#" -ge 2 ] || usage
      base_sha="$2"
      shift 2
      ;;
    --head-sha)
      [ "$#" -ge 2 ] || usage
      head_sha="$2"
      shift 2
      ;;
    *)
      usage
      ;;
  esac
done

[ -n "$repo_root" ] && [ -n "$base_ref" ] && [ -n "$base_sha" ] && [ -n "$head_sha" ] || usage

if ! command -v git >/dev/null 2>&1; then
  echo "native Codex review unavailable: git is not installed" >&2
  exit 69
fi

repo_root="$(git -C "$repo_root" rev-parse --show-toplevel 2>/dev/null)" || {
  echo "native Codex review unavailable: --repo is not a Git working tree" >&2
  exit 65
}

resolved_base="$(git -C "$repo_root" rev-parse --verify "${base_ref}^{commit}" 2>/dev/null)" || {
  echo "native Codex review unavailable: base ref cannot be resolved: $base_ref" >&2
  exit 65
}
resolved_expected_base="$(git -C "$repo_root" rev-parse --verify "${base_sha}^{commit}" 2>/dev/null)" || {
  echo "native Codex review unavailable: base SHA cannot be resolved: $base_sha" >&2
  exit 65
}
resolved_head="$(git -C "$repo_root" rev-parse --verify "${head_sha}^{commit}" 2>/dev/null)" || {
  echo "native Codex review unavailable: head SHA cannot be resolved: $head_sha" >&2
  exit 65
}

if [ "$resolved_base" != "$resolved_expected_base" ]; then
  echo "native Codex review unavailable: base ref moved after scope verification" >&2
  exit 65
fi

if ! git -C "$repo_root" merge-base "$resolved_base" "$resolved_head" >/dev/null 2>&1; then
  echo "native Codex review unavailable: base and head have no merge base" >&2
  exit 65
fi

if ! command -v codex >/dev/null 2>&1 || ! codex exec review --help >/dev/null 2>&1; then
  echo "native Codex review unavailable: codex exec review is not supported" >&2
  exit 69
fi

review_prompt="$(cat)"
if [ -z "$review_prompt" ]; then
  review_prompt="Review only defects introduced by this change. Report prioritized findings with file paths, line numbers, trigger conditions, and consequences. Do not modify files or publish comments."
fi

scratch_root="$(mktemp -d "${TMPDIR:-/tmp}/devflow-codex-review.XXXXXX")"
review_worktree="$scratch_root/worktree"

cleanup() {
  if [ -e "$review_worktree/.git" ]; then
    git -C "$repo_root" worktree remove --force "$review_worktree" >/dev/null 2>&1 || true
  fi
  rmdir "$scratch_root" >/dev/null 2>&1 || true
}

trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' HUP TERM

git -C "$repo_root" worktree add --detach --quiet "$review_worktree" "$resolved_head"

(
  cd "$review_worktree"
  printf '%s\n' "$review_prompt" | codex exec review --ephemeral --base "$base_ref" -
)
