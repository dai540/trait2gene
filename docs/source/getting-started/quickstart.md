# Quickstart

Create a config template:

```bash
trait2gene init config.toml
```

Validate it:

```bash
trait2gene validate config.toml
```

Inspect the stage plan:

```bash
trait2gene plan config.toml
```

Materialize a compact run directory:

```bash
trait2gene run config.toml
```

The result is a small output root containing only metadata and report stubs.

