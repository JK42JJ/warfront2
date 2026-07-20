"""진입점: `wf` = 훈련 시작 · `wf reset` = 기록 초기화."""
from __future__ import annotations

import typer

cli = typer.Typer(add_completion=False, invoke_without_command=True,
                  help="WARFRONT 2 — 50일 코테 합격 훈련기")


@cli.callback()
def _default(ctx: typer.Context) -> None:
    """인자 없이 실행하면 훈련 시작."""
    if ctx.invoked_subcommand is None:
        from wf.app import run
        run()


@cli.command()
def reset(
    yes: bool = typer.Option(False, "--yes", "-y", help="확인 없이 삭제"),
) -> None:
    """모든 훈련 기록 초기화 (세션·개인최고·스트릭·50일 일차 전부 삭제)."""
    from wf.store.db import DB_PATH
    if not DB_PATH.exists():
        typer.echo("기록 없음 — 이미 초기 상태입니다.")
        raise typer.Exit()
    if not yes:
        typer.confirm(
            f"⚠️  {DB_PATH} 를 삭제합니다. 세션·개인최고·연속일·50일 일차가 전부 사라집니다. 계속?",
            abort=True)
    DB_PATH.unlink()
    typer.echo("✅ 초기화 완료 — 다음 `wf` 실행이 Day 1이 됩니다.")


def main() -> None:
    cli()
