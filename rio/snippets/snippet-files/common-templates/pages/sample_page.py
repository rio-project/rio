import rio

from .. import components as comps

# TODO


class SamplePage(rio.Component):
    def build(self) -> rio.Component:
        return comps.SampleComponent()
