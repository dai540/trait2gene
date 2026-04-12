# Tutorial: Minimal Local Run

This tutorial uses no downloaded data.

1. Create a tiny summary-statistics file locally.

```text
SNP    P
rs1    0.01
```

2. Create `config.toml`.
3. Run:

```bash
trait2gene validate config.toml
trait2gene plan config.toml
trait2gene run config.toml
```

4. Inspect:

- `metadata/run-summary.json`
- `reports/summary.md`

This is the correct workflow when you want to verify repository wiring without
introducing large external assets.

