# Python API

Main public modules:

- `trait2gene.config`
- `trait2gene.pipeline`
- `trait2gene.cli`

## Core functions

```python
from trait2gene.config import load_config, validate_config, write_template
from trait2gene.pipeline import build_stage_plan, materialize_run
```

Use these functions when you want the same behavior as the CLI from Python.

