"""진입점: `wf` 한 명령."""
import typer

cli = typer.Typer(add_completion=False, help="WARFRONT 2 — 50일 코테 합격 훈련기")


@cli.command()
def main() -> None:
    """훈련 시작."""
    from wf.app import run
    run()
