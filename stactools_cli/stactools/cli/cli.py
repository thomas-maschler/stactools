import logging

import click

from stactools.cli import registry


def setup_logging(level):
    logger = logging.getLogger('stactools')
    logger.setLevel(level)

    ch = logging.StreamHandler()
    ch.setLevel(level)
    formatter = logging.Formatter('%(message)s')
    ch.setFormatter(formatter)

    logger.addHandler(ch)


@click.group()
@click.option('-v', '--verbose', help=("Use verbose mode"), is_flag=True)
@click.option('-q',
              '--quiet',
              help=("Use quiet mode (no output)"),
              is_flag=True)
def cli(verbose, quiet):
    logging_level = logging.INFO
    if verbose:
        logging_level = logging.DEBUG
    if quiet:
        logging_level = logging.ERROR
    setup_logging(logging_level)


for create_subcommand in registry.get_create_subcommand_functions():
    create_subcommand(cli)


def run_cli():
    cli(prog_name='stactools')


if __name__ == "__main__":
    run_cli()
