"""진입점: wf=훈련 · wf update=콘텐츠 최신화 · wf setup=기록 GitHub 연동 · wf reset."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import typer

PKG_ROOT = Path(__file__).resolve().parent.parent   # 설치 repo 루트 (git clone 기준)
cli = typer.Typer(add_completion=False, invoke_without_command=True,
                  help="WARFRONT 2 — 50일 코테 합격 훈련기")


def _versions() -> dict:
    meta = json.loads((Path(__file__).parent / "content/meta.json").read_text())
    from wf.content.loader import load_katas
    meta["katas"] = len(load_katas())
    return meta


@cli.callback()
def _default(ctx: typer.Context) -> None:
    """인자 없이 실행하면 훈련 시작."""
    if ctx.invoked_subcommand is None:
        from wf.app import run
        run()


@cli.command()
def version() -> None:
    """앱·콘텐츠 버전과 카타 수."""
    v = _versions()
    typer.echo(f"WARFRONT 2 v{v['app_version']} · 콘텐츠 {v['content_version']} · 카타 {v['katas']}종")


@cli.command()
def update() -> None:
    """메인 repo에서 최신 문제·기능 받기 (git clone 설치 기준)."""
    if not (PKG_ROOT / ".git").exists():
        typer.echo("git 설치본이 아닙니다. 재설치로 업데이트하세요:\n"
                   "  pip install --upgrade git+https://github.com/JK42JJ/warfront2.git")
        raise typer.Exit(1)
    before = _versions()
    r = subprocess.run(["git", "-C", str(PKG_ROOT), "pull", "--rebase", "origin", "main"],
                       capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        typer.echo(f"❌ 업데이트 실패: {r.stderr.strip().splitlines()[-1] if r.stderr else 'git 오류'}")
        raise typer.Exit(1)
    after = _versions()
    if "Already up to date" in r.stdout or before == after:
        typer.echo(f"이미 최신입니다 — 콘텐츠 {after['content_version']} · 카타 {after['katas']}종")
    else:
        typer.echo(f"✅ 업데이트 완료: 콘텐츠 {before['content_version']}→{after['content_version']}, "
                   f"카타 {before['katas']}→{after['katas']}종")


@cli.command()
def setup(repo_url: str = typer.Argument(..., help="내 기록 저장용 GitHub repo URL (본인이 만든 빈 repo)")) -> None:
    """훈련 기록을 내 GitHub repo로 자동 push하도록 설정."""
    from wf.store.db import DB_DIR
    DB_DIR.mkdir(parents=True, exist_ok=True)
    def git(*a): return subprocess.run(["git", "-C", str(DB_DIR), *a],
                                       capture_output=True, text=True, timeout=30)
    if not (DB_DIR / ".git").exists():
        git("init", "-q", "-b", "main")
    (DB_DIR / ".gitignore").write_text("wf.db\n")   # DB 원본은 로컬만, 기록 JSON만 push
    remotes = git("remote").stdout.split()
    if "origin" in remotes:
        git("remote", "set-url", "origin", repo_url)
    else:
        git("remote", "add", "origin", repo_url)
    (DB_DIR / "records").mkdir(exist_ok=True)
    typer.echo(f"✅ 기록 repo 설정 완료 → {repo_url}\n"
               f"   이제 세션이 끝날 때마다 {DB_DIR}/records/ 가 자동 push됩니다.")


@cli.command()
def reset(yes: bool = typer.Option(False, "--yes", "-y", help="확인 없이 삭제")) -> None:
    """모든 훈련 기록 초기화 (세션·개인최고·스트릭·50일 일차 전부 삭제)."""
    from wf.store.db import DB_PATH
    if not DB_PATH.exists():
        typer.echo("기록 없음 — 이미 초기 상태입니다.")
        raise typer.Exit()
    if not yes:
        typer.confirm(f"⚠️  {DB_PATH} 를 삭제합니다. 전부 사라집니다. 계속?", abort=True)
    DB_PATH.unlink()
    typer.echo("✅ 초기화 완료 — 다음 `wf` 실행이 Day 1이 됩니다.")


def main() -> None:
    cli()
