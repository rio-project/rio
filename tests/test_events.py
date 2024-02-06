from utils import create_mockapp

import rio


class ChildToggler(rio.Component):
    child: rio.Component
    switch: bool = True

    def toggle(self) -> None:
        self.switch = not self.switch

    def build(self) -> rio.Component:
        if self.switch:
            return rio.Spacer()
        else:
            return self.child


async def test_mounted():
    mounted = False
    unmounted = False

    class DemoComponent(rio.Component):
        @rio.event.on_mount
        def _on_mount(self):
            nonlocal mounted
            mounted = True

        @rio.event.on_unmount
        def _on_unmount(self):
            nonlocal unmounted
            unmounted = True

        def build(self) -> rio.Component:
            return rio.Text("hi")

    def build():
        return ChildToggler(DemoComponent())

    async with create_mockapp(build) as app:
        root = app.get_component(ChildToggler)
        assert not mounted
        assert not unmounted

        root.toggle()
        await app.refresh()
        assert mounted
        assert not unmounted

        root.toggle()
        await app.refresh()
        assert unmounted
