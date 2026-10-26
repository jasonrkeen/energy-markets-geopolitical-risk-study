"""Stage completed runs and retain the previous publication on any calculation failure."""
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import uuid4

@contextmanager
def staged_output(destination: Path):
    destination = destination.resolve()
    parent = destination.parent.resolve()
    parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix=".v2-stage-", dir=parent) as temporary:
        stage = Path(temporary) / "result"
        stage.mkdir()
        yield stage
        backup = parent / (".v2-previous-" + uuid4().hex)
        # Both rename targets are resolved children of the same intended output directory.
        if stage.resolve().parent.parent != parent or backup.resolve().parent != parent:
            raise ValueError("Unexpected publication path")
        if destination.exists():
            destination.rename(backup)
        try:
            stage.rename(destination)
        except BaseException:
            if backup.exists():
                backup.rename(destination)
            raise
        # Preserve the prior run as an ignored backup, never silently delete its evidence.
