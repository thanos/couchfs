"""Console script for couchfs."""
import sys
import pprint
import click
import couchfs
import humanize
import tabulate
import os, stat
from shutil import *
import pathlib

@click.group()
def cli():
    pass

@click.command()
def ls():
    rows = []
    max_len = 0
    for file_path, size in couchfs.CouchDBClient().ls():
        max_len = max(max_len, len(file_path))
        rows.append((file_path, size))
    ftr = '{file_path:%d} {size:>10}' % (max_len+3)
    for file_path, size in rows:
        click.echo(ftr.format(file_path=file_path, size=humanize.naturalsize(size)))






@cli.command(short_help="upload files.")
@click.option(
    "--doc_per_path", is_flag=False, help="forcibly copy over an existing managed file"
)
@click.option(
    "--dry_run", is_flag=True, help="forcibly copy over an existing managed file"
)
@click.argument("src", type=click.Path())
@click.argument("dst", type=click.Path())
def upload(src, dst, doc_per_path, dry_run):
    """uploads from src to dst.
    """
    for src, dst, status,reason in couchfs.CouchDBClient().upload(src, dst, dry_run):
        click.echo(f'{src} {dst} {status}:{reason}')
cli.add_command(ls)
cli.add_command(upload)

@cli.command(short_help="upload files.")
@click.option(
    "--doc_per_path", is_flag=False, help="forcibly copy over an existing managed file"
)
@click.option(
    "--dry_run", is_flag=False, help="forcibly copy over an existing managed file"
)
@click.argument("src", type=click.Path())
@click.argument("dst", type=click.Path())
def download(src, dst, doc_per_path, dry_run):
    """uploads from src to dst.
    """
    for src, dst, status,reason in couchfs.CouchDBClient().download(src, dst):
        click.echo(f'{src} {dst} {status}:{reason}')

    # for src, dst, status,reason in couchfs.CouchDBClient().download(src, dst):
    #     click.echo(f'{src} {dst} {status}:{reason}')
cli.add_command(ls)
cli.add_command(upload)
cli.add_command(download)


@click.command()
def main(args=None):
    """Console script for couchfs."""
    click.echo("Replace this message by putting your code into "
               "couchfs.cli.main")
    click.echo("See click documentation at https://click.palletsprojects.com/")
    return 0


if __name__ == "__main__":
    sys.exit(cli())  # pragma: no cover
