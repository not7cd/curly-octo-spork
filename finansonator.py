import click
import dokuwiki
import crayons
import os

from datetime import datetime
from jinja2 import Template
from tabulate import tabulate

report_page = Template(
    """
===== {{ title }} =====

{{ table }}
\n\n
"""
)


WIKI_URL = "https://wiki.hs3.pl"
WIKI_PAGE = ":finanse:bilanse"


def aggregate_data():
    return [("przychody", 1000), ("wydatki", -700), ("bilans", 300)]


# TODO: https://docs.python.org/3/library/getpass.html#getpass.getpass

@click.command()
@click.option("--user", prompt="Username", default=lambda: os.environ.get("USER", ""))
@click.option(
    "--password",
    prompt="password",
    hide_input=True,
    default=lambda: os.environ.get("PASSWORD", ""),
)
def connect(user, password):
    """Simple program that greets NAME for a total of COUNT times."""

    try:
        wiki = dokuwiki.DokuWiki(WIKI_URL, user, password)
    except dokuwiki.DokuWikiError as exc:
        print(crayons.red(exc))
    else:
        print(crayons.green("Connected to {}".format(wiki.title)))

    print(crayons.yellow("Rendering template"))

    content = report_page.render(
        title=datetime.today(), table=tabulate(aggregate_data(), tablefmt="youtrack")
    )

    print(content)

    print(crayons.yellow("Appending to wiki page {}".format(WIKI_PAGE)))
    wiki.pages.append(WIKI_PAGE, content=content)


if __name__ == "__main__":
    connect()
