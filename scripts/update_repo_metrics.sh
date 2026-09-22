#!/usr/bin/env bash
set -euo pipefail

OWNER="DiwasKhatri07"
REPO="NepaliLang"
API="https://api.github.com/repos/${OWNER}/${REPO}"
OUT_DIR="docs/assets"
mkdir -p "$OUT_DIR"

api_get() {
  curl --fail --silent --show-error \
    -H "Accept: application/vnd.github+json" \
    -H "Authorization: Bearer ${GITHUB_TOKEN:-}" \
    -H "X-GitHub-Api-Version: 2022-11-28" "$1"
}

repo_json="$(api_get "$API")"
cutoff="$(date -u -d '30 days ago' '+%Y-%m-%dT%H:%M:%SZ')"
commits_json="$(api_get "https://api.github.com/search/commits?q=repo:${OWNER}/${REPO}+committer-date:%3E${cutoff}&per_page=1")"
issues_json="$(api_get "https://api.github.com/search/issues?q=repo:${OWNER}/${REPO}+is:issue+is:open&per_page=1")"
prs_json="$(api_get "https://api.github.com/search/issues?q=repo:${OWNER}/${REPO}+is:pr+is:open&per_page=1")"
releases_json="$(api_get "$API/releases?per_page=100")"

stars="$(jq -r '.stargazers_count' <<<"$repo_json")"
forks="$(jq -r '.forks_count' <<<"$repo_json")"
watchers="$(jq -r '.subscribers_count' <<<"$repo_json")"
repo_size="$(jq -r '.size' <<<"$repo_json")"
open_issues="$(jq -r '.total_count' <<<"$issues_json")"
open_prs="$(jq -r '.total_count' <<<"$prs_json")"
commits_30d="$(jq -r '.total_count' <<<"$commits_json")"
releases="$(jq 'length' <<<"$releases_json")"
jq -n \
  --argjson stars "$stars" \
  --argjson forks "$forks" \
  --argjson watchers "$watchers" \
  --argjson repo_size_kb "$repo_size" \
  --argjson open_issues "$open_issues" \
  --argjson open_prs "$open_prs" \
  --argjson commits_30d "$commits_30d" \
  --argjson releases "$releases" \
  '{project:"NepaliCode", repository:"DiwasKhatri07/NepaliLang", refresh_schedule:"every 30 minutes", metrics:{stars:$stars, forks:$forks, watchers:$watchers, open_issues:$open_issues, open_pull_requests:$open_prs, commits_last_30_days:$commits_30d, releases:$releases, repository_size_kb:$repo_size_kb}}' \
  > "$OUT_DIR/repo-metrics.json"

cat > "$OUT_DIR/repo-metrics.svg" <<SVG
<svg xmlns="http://www.w3.org/2000/svg" width="920" height="230" viewBox="0 0 920 230" role="img" aria-labelledby="title desc">
  <title id="title">NepaliCode repository metrics</title>
  <desc id="desc">Live repository statistics for DiwasKhatri07 NepaliLang, refreshed every 30 minutes.</desc>
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#101827"/><stop offset="1" stop-color="#1d2d46"/></linearGradient>
    <linearGradient id="accent" x1="0" y1="0" x2="1" y2="0"><stop stop-color="#dc143c"/><stop offset="1" stop-color="#f97316"/></linearGradient>
  </defs>
  <rect width="920" height="230" rx="20" fill="url(#bg)"/>
  <rect x="0" y="0" width="920" height="7" rx="3" fill="url(#accent)"/>
  <text x="34" y="48" fill="#f8fafc" font-family="Arial, sans-serif" font-size="25" font-weight="700">NepaliCode · live repository metrics</text>
  <text x="34" y="74" fill="#a9b7ca" font-family="Arial, sans-serif" font-size="14">DiwasKhatri07/NepaliLang · refreshed every 30 minutes</text>
  <g font-family="Arial, sans-serif">
    <rect x="34" y="98" width="98" height="78" rx="12" fill="#ffffff12"/><text x="50" y="126" fill="#fda4af" font-size="13">STARS</text><text x="50" y="158" fill="#fff" font-size="25" font-weight="700">$stars</text>
    <rect x="145" y="98" width="98" height="78" rx="12" fill="#ffffff12"/><text x="161" y="126" fill="#fda4af" font-size="13">FORKS</text><text x="161" y="158" fill="#fff" font-size="25" font-weight="700">$forks</text>
    <rect x="256" y="98" width="98" height="78" rx="12" fill="#ffffff12"/><text x="272" y="126" fill="#fda4af" font-size="13">WATCHERS</text><text x="272" y="158" fill="#fff" font-size="25" font-weight="700">$watchers</text>
    <rect x="367" y="98" width="98" height="78" rx="12" fill="#ffffff12"/><text x="383" y="126" fill="#fda4af" font-size="13">OPEN ISSUES</text><text x="383" y="158" fill="#fff" font-size="25" font-weight="700">$open_issues</text>
    <rect x="478" y="98" width="98" height="78" rx="12" fill="#ffffff12"/><text x="494" y="126" fill="#fda4af" font-size="13">OPEN PRs</text><text x="494" y="158" fill="#fff" font-size="25" font-weight="700">$open_prs</text>
    <rect x="589" y="98" width="112" height="78" rx="12" fill="#ffffff12"/><text x="605" y="126" fill="#fda4af" font-size="13">COMMITS / 30D</text><text x="605" y="158" fill="#fff" font-size="25" font-weight="700">$commits_30d</text>
    <rect x="714" y="98" width="86" height="78" rx="12" fill="#ffffff12"/><text x="730" y="126" fill="#fda4af" font-size="13">RELEASES</text><text x="730" y="158" fill="#fff" font-size="25" font-weight="700">$releases</text>
  </g>
  <text x="34" y="207" fill="#7f91a8" font-family="Arial, sans-serif" font-size="12">Repository size: ${repo_size} KB · Source: GitHub REST API · Refresh schedule: every 30 minutes</text>
</svg>
SVG
