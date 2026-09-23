# Recommended terminal shortcuts

Agent Manager reads every `aliases/*.json` file here as recommended shell aliases when this
repository is one of its skill sources. They appear as "recommended · add" on its terminal
shortcuts page; nothing is written to `~/.zshrc` or `~/.zprofile` until the user adds one, and a
name the user already defines anywhere in those files is not recommended.

Each file has this shape:

```json
{
  "timezone": "America/Los_Angeles",
  "lang": "en_US.UTF-8",
  "aliases": { "claude": "TZ=\"{timezone}\" LANG=\"{lang}\" LC_ALL=\"{lang}\" claude" }
}
```

- `{timezone}` and `{lang}` in a value are replaced with that file's `timezone` and `lang`
  before the alias is shown or written.
- Names start with a letter or `_` and use only letters, digits, `_` and `-`.
- Values are written as `alias name='value'`, so they cannot contain a single quote or a newline.
- When two files define the same name, the first file in name order wins.
- Keep permission-skipping flags out of the defaults; users add them per alias.

`tests/test_alias_contracts.py` checks these rules offline. This file moved here from the
`agent-manager` repository (`config/shell-aliases.json`) on 2026-09-23.
