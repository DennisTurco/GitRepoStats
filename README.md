![logo](./imgs/banner.png)

## Description

**Git Repo Stats** is a Windows desktop application with a modern, user-friendly graphical interface that allows you to generate reports and analyze key information about the lifecycle of any GitHub project you scan.

With Git Repo Stats, you can:

- **Development Team Management and Monitoring**
  - Get an instant overview of each developer's contributions.
- **General Project Health Overview**
  - Track historical activity and trends over time.
- **Productivity Analysis**
  - Analyze contributions per author, including commits, lines added/removed, and files modified.
- **Code Review Support for Project Managers**
  - Identify files that may require refactoring.
  - Monitor the most active authors in each module to assign code reviews more effectively.
- **Code Complexity Analysis**
  - Detect functions that are well-written or may need improvement.

| ![image1](./docs/imgs/screenshot1.png) | ![image2](./docs/imgs/screenshot2.png) |
| ------------------------ | ------------------------ |
| ![image3](./docs/imgs/screenshot3.png) | ![image4](./docs/imgs/screenshot4.png) |
| ![image5](./docs/imgs/screenshot5.png) |  |

### Example Output

View an example report generated [📄 Redis stats example .html](./docs/redis_stats_example.html) from scanning redis repo (you can view the github project of redis from [here](https://github.com/redis/redis))

## Usage

The tool works with both public and private repositories.
The only requirement is that you are able to clone the repository on your local machine.

1. Clone this project: `git clone https://github.com/DennisTurco/GitRepoStats.git`
2. Run GitRepoStats from the main file (gitrepostats.py)
3. in "Workspace path" field, insert the absolute path of the GitHub project root you want to scan.
4. Press the "Get stats" button to start the project analysis.

Note: *The larger the project (and the fewer filters you apply), the longer the analysis will take.*

## 🐛 Report a BUG

To report a BUG -> [ISSUE](https://github.com/DennisTurco/GitRepoStats/issues)

## Licence

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)

## Authors

- [DennisTurco](https://www.github.com/DennisTurco)

## Support

For support, email: [dennisturco@gmail.com](dennisturco@gmail.com)
