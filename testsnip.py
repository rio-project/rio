import rio.snippets

result = rio.snippets.get_snippet_section(
    "example-counter/simple_counter_app.py",
    section="run",
)

print(result)
