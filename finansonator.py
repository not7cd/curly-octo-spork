from datetime import datetime
from getpass import getpass


import csv
import click
import crayons
import dokuwiki
import tablib
from jinja2 import Template
from tabulate import tabulate
from glom import glom

from helpers import _normalize_mbank_headers, report_balance, report_date, last_balance

from collections import defaultdict

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
        title="{}.{}".format(report["year"], report["month"]),
        table=tabulate(list(report.items())[:-2], tablefmt="youtrack"),
    )

    print(content)

    if not dry_run:
        print(crayons.green("Appending to wiki page {} DokuWiki".format(WIKI_PAGE)))
        wiki.pages.append(WIKI_PAGE, content=content)
    else:
        print(crayons.yellow("Would append to page {} at DokuWiki".format(WIKI_PAGE)))


@click.group()
@click.option("-v", "--verbose", is_flag=True)
@click.option("-n", "--dry-run", is_flag=True)
@click.pass_context
def cli(ctx, verbose, dry_run):
    ctx.obj['VERBOSE'] = verbose
    ctx.obj['DRY_RUN'] = dry_run


def file_export_format(file):
    return 'csv'


def detect_scheme(file):
    return "mbank"


def _normalize_float(string):
    return float(string.strip().replace(",", ".").replace(" ", ""))


specs = {
    "mbank": {
        "date": lambda r: datetime.strptime(r["#Data operacji"], "%Y-%m-%d"),
        "amount": lambda r: _normalize_float(r["#Kwota"]),
        "balance": lambda r: _normalize_float(r["#Saldo po operacji"])
    }
}


@cli.command()
@click.option("-i", "--input", "src", type=click.File("r"))
@click.option("-o", "--output", "dst", type=click.File("w"))
@click.pass_context
def aggregate(ctx, src, dst):
    data = []
    src = [src]
    for file in src:
        print(dir(dst))
        if file is not None:
            scheme = detect_scheme(file)
            spec = specs[scheme]

            reader = csv.DictReader(file, delimiter=";")
            for row in reader:
                print(row)
                normalized_row = glom(row, spec)
                data.append(normalized_row)

    aggregated = defaultdict(lambda: [0, 0, 0])

    for row in data:
        revenue = row["amount"] if row["amount"] > 0 else 0
        expenses = row["amount"] if row["amount"] < 0 else 0
        aggregated[(row["date"].year, row["date"].month)][0] += revenue
        aggregated[(row["date"].year, row["date"].month)][1] += expenses
        aggregated[(row["date"].year, row["date"].month)][2] += row["amount"]
        print(aggregated[(row["date"].year, row["date"].month)])

    aggregated_dataset = tablib.Dataset()
    aggregated_dataset.headers = ["year", "month", "revenue", "expenses", "balance"]
    for date in aggregated:
        aggregated_dataset.append([*date, *aggregated[date]])

    if dst is not None:
        print(dir(dst))
        dst.write(aggregated_dataset.export(file_export_format(dst)))

if __name__ == "__main__":
    cli(obj={})
