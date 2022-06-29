import sys
from importlib import import_module
from pathlib import Path
from zipfile import ZipFile

import click

from questionpy.sdk.manifest import Manifest
from questionpy.sdk.registry import registry

run: click.Command


@click.command()
@click.argument("package", type=click.Path(exists=True, dir_okay=False, path_type=Path))
def run(package: Path):
    with ZipFile(package) as package_file:
        manifest = Manifest.parse_raw(package_file.read("qpy_manifest.json"))

    print(registry)

    old_path = sys.path
    sys.path = [str(package), str(package / "dependencies")]
    try:
        import_module(manifest.entrypoint)
    finally:
        sys.path = old_path

    print(registry)
