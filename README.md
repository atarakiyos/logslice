# logslice

A fast CLI tool for filtering and slicing structured log files by time range, level, or field patterns.

---

## Installation

```bash
pip install logslice
```

Or install from source:

```bash
git clone https://github.com/yourname/logslice.git && cd logslice && pip install .
```

---

## Usage

```bash
# Filter logs by time range
logslice app.log --from "2024-01-15T08:00:00" --to "2024-01-15T09:00:00"

# Filter by log level
logslice app.log --level ERROR

# Filter by a specific field pattern
logslice app.log --field "user_id=42"

# Combine filters and output to a file
logslice app.log --from "2024-01-15T08:00:00" --level WARN --field "service=api" -o output.log
```

### Options

| Flag | Description |
|------|-------------|
| `--from` | Start of time range (ISO 8601) |
| `--to` | End of time range (ISO 8601) |
| `--level` | Minimum log level (`DEBUG`, `INFO`, `WARN`, `ERROR`) |
| `--field` | Key-value field pattern to match |
| `-o, --output` | Write results to a file instead of stdout |
| `--format` | Input format: `json`, `logfmt`, or `auto` (default: `auto`) |

---

## Supported Formats

- **JSON** — one JSON object per line (e.g., structured logs from Logrus, Zap)
- **logfmt** — `key=value` pairs (e.g., output from Heroku, Go services)

---

## Contributing

Pull requests are welcome. Please open an issue first to discuss any major changes.

---

## License

MIT © 2024 [yourname](https://github.com/yourname)