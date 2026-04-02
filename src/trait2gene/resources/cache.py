from pathlib import Path

from platformdirs import user_cache_dir

from trait2gene.config.defaults import DEFAULT_CACHE_APPNAME


def get_cache_dir() -> Path:
    cache_dir = Path(user_cache_dir(DEFAULT_CACHE_APPNAME)).expanduser()
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir
