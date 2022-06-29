import click as click

from questionpy.sdk.commands.package import package
from questionpy.sdk.commands.run import run


@click.group()
def cli():
    pass


cli.add_command(package)
cli.add_command(run)

if __name__ == '__main__':
    cli()
