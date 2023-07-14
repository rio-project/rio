import webbrowser
from pathlib import Path

import coverage
import pytest

cov = coverage.Coverage(branch=True, source=["reflex"])
cov.start()

pytest.main(["tests"])

cov.stop()
cov.save()

cov.html_report()
html_path = Path(__file__).parent / "htmlcov" / "index.html"
webbrowser.open(html_path.as_uri())
