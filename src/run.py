import os

import django

# Инициализируем Django до инициализации приложения:
os.environ["DJANGO_SETTINGS_MODULE"] = "pocket_storage.settings"
django.setup()

import click
import uvicorn

from django.core import management
from django.conf import settings
import pocket_storage.app


@click.group()
def cli():
    pass


@cli.command()
@click.option(
    "--collectstatic/--no-collectstatic",
    is_flag=True,
    default=True,
    help="collect Django static",
)
@click.option(
    "--uvicorn-debug/--no-uvicorn-debug",
    is_flag=True,
    default=True,
    help="Enable/Disable debug and auto-reload",
)
@click.option(
    "--migrate/--no-migrate",
    is_flag=True,
    default=False,
    help="Apply migrations before run app",
)
def web(collectstatic: bool, uvicorn_debug: bool, migrate: bool):
    if migrate:
        management.call_command("migrate")

    if collectstatic:
        management.call_command("collectstatic", "--no-input", "--clear")

    app = pocket_storage.app.app

    if uvicorn_debug:
        app = "pocket_storage.app:app"

    uvicorn.run(
        # TODO: add uvicorn_debug
        app,
        host=settings.HOST,
        port=settings.PORT,
        access_log=False,
        log_config=None,
        lifespan="on",
        loop="uvloop",
    )


if __name__ == "__main__":
    cli()
