import subprocess
import sys


def test_cli_status():
    result = subprocess.run(
        [sys.executable, "-m", "src.main", "status"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert "Emuesiri Jessica Agbabune" in result.stdout
    assert "TD Africa" in result.stdout
    assert "Succession Planning" in result.stdout


def test_cli_weekly_dry_run():
    result = subprocess.run(
        [sys.executable, "-m", "src.main", "run", "--type", "weekly", "--dry-run"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert "MY TALENT GROWTH PLAN" in result.stdout
    assert "1. IMMEDIATE L&D SKILL" in result.stdout
    assert "TD AFRICA APPLICATION" in result.stdout
