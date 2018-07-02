from datetime import datetime
from getpass import getpass

import click
import crayons
import dokuwiki
import tablib
from jinja2 import Template
from tabulate import tabulate

from helpers import _normalize_mbank_headers, report_balance, report_date, \
    last_balance

cli = click.Group()

report_page = Template(
    """
===== {{ title }} =====

{{ table }}
\n\n
"""
)

WIKI_URL = "https://wiki.hs3.pl"
WIKI_PAGE = ":finanse:bilanse"


def create_wiki_session():
    """returns dokuwiki session, aiming for safer experience"""
    print(crayons.yellow("Enter credentials for {}".format(WIKI_URL)))
    user = input("User: ")
    password = getpass("Password: ")

    try:
        wiki = dokuwiki.DokuWiki(WIKI_URL, user, password)
    except dokuwiki.DokuWikiError as exc:
        print(crayons.red(exc))
        exit()
    else:
        print(crayons.green("Connected to {}".format(wiki.title)))
        return wiki



@click.option("--dry-run", "dry_run", is_flag=True)
def post_report(wiki, dry_run, report):
    """Simple program that greets NAME for a total of COUNT times."""
    content = report_page.render(
        title="{}.{}".format(report["year"], report["month"]), table=tabulate(list(report.items())[:-2], tablefmt="youtrack")
    )

    print(content)

    if not dry_run:
        print(crayons.green("Appending to wiki page {} DokuWiki".format(WIKI_PAGE)))
        wiki.pages.append(WIKI_PAGE, content=content)
    else:
        print(crayons.yellow("Would append to page {} at DokuWiki".format(WIKI_PAGE)))


@click.option("-i", "--input", "src", type=click.File("r"))
@click.option("-v", "--verbose", is_flag=True, help="Enables verbose mode")
@click.option(
    "-n", "--dry-run", is_flag=True, help="Will print out changes without applying them"
)
def aggregate(src, verbose, dry_run):
    if src is not None:
        data = tablib.import_set(src.read(), "csv", delimiter=";")
        data.headers = _normalize_mbank_headers(data.headers)

        aggregated = {**report_balance(data), **report_date(data), "balance": last_balance(data)}

        if verbose:
            click.echo(aggregated)
        return aggregated


@click.command()
@click.option("-i", "--input", "src", type=click.File("r"))
@click.option("-v", "--verbose", is_flag=True, help="Enables verbose mode")
@click.option(
    "-n", "--dry-run", is_flag=True, help="Will print out changes without applying them"
)
def main(src, dry_run, verbose):
    report = aggregate(src, verbose, dry_run)

    wiki = create_wiki_session()
    post_report(wiki=wiki, dry_run=dry_run, report=report)


if __name__ == "__main__":
    main()
