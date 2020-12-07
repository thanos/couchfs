"""Console script for couchfs."""
import sys

import click
import humanize

from couchfs import api


@click.group()
def cli():
    pass

@click.command()
def init():
    api.CouchDBClient.init_db(logger=click.echo)


@click.command()
@click.argument('patterns', nargs=-1)
def ls(patterns):
    rows = []
    max_len = 0
    for file_path, size in api.CouchDBClient().list_attachments(*patterns):
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
    for src, dst, status,reason in api.CouchDBClient().upload(src, dst, dry_run):
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
    for src, dst, status,reason in api.CouchDBClient().download(src, dst):
        click.echo(f'{src} {dst} {status}:{reason}')

    # for src, dst, status,reason in couchfs.CouchDBClient().download(src, dst):
    #     click.echo(f'{src} {dst} {status}:{reason}')
cli.add_command(ls)
cli.add_command(upload)
cli.add_command(download)
cli.add_command(init)




if __name__ == "__main__":
    sys.exit(cli())  # pragma: no cover
