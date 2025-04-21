# cli.py
import click
import subprocess
import sys
import os

BASE = os.path.dirname(__file__)

@click.group()
def cli():
    """TaskFlow Manager CLI."""
    pass

@cli.command()
def up():
    """
    Levanta los tres servicios:
    1) API FastAPI en :2410
    2) MCP server (stdio)
    3) Frontend (server.js) en :3000
    """
    procs = []
    try:
        # 1) FastAPI
        procs.append(subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "api:app", "--port", "2410", "--reload"],
            cwd=BASE
        ))

        # 2) MCP (stdio)
        procs.append(subprocess.Popen(
            [sys.executable, "mcp_server.py"],
            cwd=BASE
        ))

        # 3) Frontend static
        procs.append(subprocess.Popen(
            ["node", "server.js"],
            cwd=BASE
        ))

        click.echo("🟢 TaskFlow UP: API→2410  MCP→stdio  Frontend→3000")
        for p in procs:
            p.wait()
    except KeyboardInterrupt:
        click.echo("\n🔴 Apagando TaskFlow...")
        for p in procs:
            p.terminate()
        sys.exit(0)

if __name__ == "__main__":
    cli()
