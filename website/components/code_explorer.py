import rio

from .. import theme


class CodeExplorer(rio.Component):
    code: str

    def build(self) -> rio.Component:
        return rio.Row(
            rio.MarkdownView(
                f"""
```python
{rio.escape_markdown_code(self.code)}
```
""",
                width=40,
                align_y=0.5,
            ),
            rio.Spacer(),
            rio.Card(
                rio.Text("Placeholder"),
                width=theme.COLUMN_WIDTH,
                height=20,
                align_y=0.5,
                margin_left=3,
            ),
        )
