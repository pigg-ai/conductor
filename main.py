import typer

from openai import OpenAI


app = typer.Typer()


@app.command()
def main() -> None:
    pass


if __name__ == "__main__":
    app()
