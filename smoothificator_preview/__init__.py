"""Separate read-only research plugin; importing outside Orca registers nothing."""
try:
    import orca
except ModuleNotFoundError as error:
    if error.name != "orca":
        raise
else:
    from . import entrypoint
