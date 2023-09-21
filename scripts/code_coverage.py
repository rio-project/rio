import sys
import webbrowser
from pathlib import Path

import coverage
import pytest

cov = coverage.Coverage(branch=True, source=["rio"])
cov.start()

pytest.main(["tests"])

cov.stop()
cov.save()

cov.html_report()

if "--no-open" not in sys.argv:
    html_path = Path(__file__).parent / "htmlcov" / "index.html"
    webbrowser.open(html_path.as_uri())
