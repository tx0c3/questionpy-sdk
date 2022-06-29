from pathlib import Path
from typing import Optional
from zipfile import PyZipFile

import click as click

from questionpy.sdk.manifest import Manifest

package: click.Command


@click.command()
@click.argument("source", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--manifest", "-m", "manifest_path", type=click.Path(exists=True, dir_okay=False, path_type=Path))
def package(source: Path, manifest_path: Optional[Path]):
    out_path = source.with_suffix(".zip")

    if not manifest_path:
        manifest_path = source / "qpy_manifest.json"

    if not manifest_path.is_file():
        raise FileNotFoundError(manifest_path)

    manifest = Manifest.parse_file(manifest_path)

    with PyZipFile(out_path.open("wb"), "w") as out_file:
        for path in source.glob("**/*.py"):
            path_in_pkg = path.relative_to(source)
            print(f"{path_in_pkg}: {path}")
            out_file.write(path, path.relative_to(source))

        print(f"qpy_manifest.json: {manifest}")
        out_file.writestr("qpy_manifest.json", manifest.json(indent=2))
