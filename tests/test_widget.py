
from web_gui import Text


def test_initial_dirty_value():
    widget = Text('foo')
    assert widget._dirty


def test_dirty_flag():
    widget = Text('foo')
    widget._dirty = False

    widget.text = 'bar'
    assert widget._dirty
