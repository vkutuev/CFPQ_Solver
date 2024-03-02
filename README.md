[![License](https://img.shields.io/badge/license-MIT-blue)](https://github.com/vkutuev/FLPQ_Solver/blob/master/LICENSE)

## Installation

### Get source code

The following code snippet downloads project source code repository, and enters project root folder. Must be executed
from the folder where you want to locate project.

```shell
git clone https://github.com/vkutuev/FLPQ_Solver.git
cd FLPQ_Solver
```

### pre-commit

#### Install

```shell
pip install pre-commit==2.15.0
pre-commit install
```

#### Run manually

```shell
pre-commit run --all-files --color always --verbose
```

## Project structure

| Entry                       | Description                             |
|:----------------------------|:----------------------------------------|
| `📁 .github`                | CI/CD scripts and GitHub related files  |
| `📁 cfpq_solver`            | Library source code                     |
| `📁 tests`                  | Library tests                           |
| `📄 .pre-commit-config.yml` | Configuration file for pre-commit hooks |
| `📄 .flake8`                | Flake8 configuration file               |
| `📄 pyproject.toml`         | Project configuration file              |
| `📄 LICENCE`                | MIT License text                        |

## License

This project licensed under MIT License. License text can be found in the
[license file](https://github.com/vkutuev/FLPQ_Solver/blob/master/LICENSE).
