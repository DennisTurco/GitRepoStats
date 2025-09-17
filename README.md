
# Git Repo Stats

## Description

...

### How i'm getting the data?

| Purpose                                          | Command                                                                            | Description                                                                                                     |
| ------------------------------------------------ | ---------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| Commit count per author                          | `git shortlog -s -n`                                                               | List of commits per author, sorted descending.                                                                  |
| Total commit count                               | `git rev-list HEAD --count`                                                        | Total number of commits in the repo. For a specific author: `git rev-list HEAD --author="Author Name" --count`. |
| Insertions/deletions per commit (summary)        | `git log --shortstat`                                                              | For each commit, shows number of files changed, insertions, deletions.                                          |
| Insertions/deletions per file (machine-friendly) | `git log --numstat`                                                                | Shows insertions and deletions per file per commit, easy to parse.                                              |
| Author + commit stats                            | `git log --format="%an" --shortstat` <br>or<br> `git log --format="%an" --numstat` | Associates each commit with its author and stats.                                                               |
| Filter by author                                 | `git log --author="Author Name" [other options]`                                   | Same as above but only for one author (works with `--numstat`, `--shortstat`, `--since`, `--until`, etc.).      |
| Most modified files (frequency)                  | `git log --name-only --pretty=format:""`                                           | Lists all files touched by commits; count occurrences to find top modified files.                               |
| Total lines added/removed by author              | `git log --author="Author Name" --oneline --shortstat`                             | Combine with `grep`/`awk` to sum total insertions and deletions for that author.                                |
| Changes between two commits                      | `git diff --stat <sha1> <sha2>` <br>or<br> `git diff --numstat <sha1> <sha2>`      | Shows changes (insertions/deletions) between two specific commits.                                              |


## Installation

- ...

## 🐛 Report a BUG

To report a BUG -> [ISSUE](https://github.com/DennisTurco/GitRepoStats/issues)

## Licence

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)

## Time report

[![wakatime](https://wakatime.com/badge/user/ce36d0fc-2f0b-4e85-b318-872804ab18b6/project/6a2e8ba4-e41d-4ee4-bb83-20ca19fe3dfb.svg)](https://wakatime.com/badge/user/ce36d0fc-2f0b-4e85-b318-872804ab18b6/project/6a2e8ba4-e41d-4ee4-bb83-20ca19fe3dfb)

## Authors

- [DennisTurco](https://www.github.com/DennisTurco)

## Support

For support, email: [dennisturco@gmail.com](dennisturco@gmail.com)
