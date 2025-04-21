import os
import subprocess
import sys

import click

BASE = os.path.dirname(__file__)


@click.group()
def cli():
    """TaskFlow Manager CLI."""
    pass


@cli.command()
@click.option(
    "--open",
    "open_browser",
    is_flag=True,
    help="Abrir navegador automáticamente.",
)
def up(open_browser):
    """Levanta API, MCP y Frontend (opcional: abrir navegador)."""
    procs = []
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    try:
        # Instalar dependencias Node.js si es necesario
        node_modules_path = os.path.join(base_dir, "node_modules")
        if not os.path.exists(node_modules_path):
            click.echo("📦 Instalando dependencias Node.js...")
            subprocess.check_call(
                ["npm", "install"],
                cwd=base_dir,
            )

        # 1. Backend API
        procs.append(
            subprocess.Popen(
                [
                    sys.executable,
                    "-m",
                    "uvicorn",
                    "taskflow_manager.api:app",
                    "--port",
                    "2410",
                    "--reload",
                ],
                cwd=base_dir,
            )
        )

        # 2. MCP Server
        procs.append(
            subprocess.Popen(
                [
                    sys.executable,
                    "-m",
                    "taskflow_manager.mcp_server",
                ],
                cwd=base_dir,
            )
        )

        # 3. Frontend estático
        procs.append(
            subprocess.Popen(
                ["node", "taskflow_manager/server.js"],
                cwd=base_dir,
            )
        )

        click.echo("🟢 TaskFlow UP: API→2410  MCP→stdio  Frontend→2411")

        if open_browser:
            import webbrowser

            webbrowser.open("http://localhost:2411")

        for p in procs:
            p.wait()

    except KeyboardInterrupt:
        click.echo("\n🔴 Apagando TaskFlow...")
        for p in procs:
            p.terminate()
        sys.exit(0)


@cli.command()
def dev():
    """Levanta solo el backend FastAPI con autoreload (modo desarrollo)."""
    click.echo("⚙️ Starting Backend on " "http://localhost:2410 ...")
    subprocess.run(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "taskflow_manager.api:app",
            "--port",
            "2410",
            "--reload",
        ]
    )


@cli.command()
def check():
    """Corre validaciones estáticas: lint, formatting y errores comunes."""
    click.echo(
        "🧪 Ejecutando validaciones con flake8, black, "
        "isort y análisis personalizado..."
    )
    subprocess.run(["flake8", "taskflow_manager"])
    subprocess.run(["black", "--check", "taskflow_manager"])
    subprocess.run(["isort", "--check-only", "taskflow_manager"])
    subprocess.run(
        [
            sys.executable,
            "test/check_field_conflicts.py",
        ]
    )


if __name__ == "__main__":
    cli()
