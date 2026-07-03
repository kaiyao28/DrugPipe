from typer.testing import CliRunner

from osteo_target_gwas.cli import app


COMMANDS = [
    "validate",
    "qc",
    "define-loci",
    "finemap",
    "map-genes",
    "coloc",
    "bone-context",
    "pathway",
    "mr-targets",
    "mediation-mr",
    "phe-mr",
    "druggability",
    "score-targets",
    "report",
    "make-target-cards",
    "run",
]


def test_cli_help_runs() -> None:
    result = CliRunner().invoke(app, ["--help"])

    assert result.exit_code == 0


def test_all_commands_appear_in_help() -> None:
    result = CliRunner().invoke(app, ["--help"])

    assert result.exit_code == 0
    for command in COMMANDS:
        assert command in result.output


def test_placeholder_commands_run() -> None:
    runner = CliRunner()

    for command in COMMANDS:
        result = runner.invoke(app, [command])

        assert result.exit_code == 0
        assert f"The '{command}' command exists but is not implemented yet." in result.output
