from typing import *  # type: ignore

import revel
from typing_extensions import TypeAlias

import rio

app = revel.App()


templates_literal: TypeAlias = Literal["biography"]
available_templates: Set[str] = set(get_args(templates_literal))


@app.command
def new(
    name: str,
    *,
    type: Literal["app", "website"],
    template: Optional[templates_literal] = None,
) -> None:
    print("new", name, type, template)


@app.command
def run(
    *,
    port: int = 8080,
    public: bool = False,
) -> None:
    print("run", port, public)


if __name__ == "__main__":
    app.run()
