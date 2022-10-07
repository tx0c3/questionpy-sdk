import logging
from pathlib import Path
from shutil import copytree
from importlib.resources import files, as_file

import click
import yaml
import example

log = logging.getLogger(__name__)


@click.command()
@click.argument("short_name", type=click.Path(exists=False, path_type=Path))
def create(short_name: Path) -> None:
    template = files(example)

    if short_name.is_dir():
        raise FileExistsError(short_name)

    with as_file(template) as template_path:
        copytree(template_path, short_name)

    manifest_path = short_name.joinpath("qpy_manifest.yml")

    with manifest_path.open("r") as manifest_f:
        manifest = yaml.safe_load(manifest_f)

    manifest["short_name"] = short_name.name

    with manifest_path.open("w") as manifest_f:
        yaml.dump(manifest, manifest_f, sort_keys=False)
