# Python Repository Template

This is a template repository to help me make Python projects with my preferred technologies configured out of the box:
* [pre-commit](https://pre-commit.com/) hooks
* [pytest](https://docs.pytest.org/en/stable/)
* [GitHub Workflows](https://docs.github.com/en/actions/concepts/workflows-and-actions/workflows)

The only dependency is [uv](https://docs.astral.sh/uv/), which you can install by following [these instructions](https://docs.astral.sh/uv/getting-started/installation/). Then, you can run [setup.sh](https://github.com/samlowe106/PythonTemplate/blob/main/setup.sh).

From there, you only need to

- [ ] edit the repo details in pyproject.toml,
- [ ] `uv add` any additional dependencies,
- [ ] customize pre-commit hooks in `.pre-commit-config.yaml`,
- [ ] edit the .gitignore file,
- [ ] edit this README, and
- [ ] set your license
