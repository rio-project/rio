import rio
import rio.cli

from ...components import component_tree
from . import component_details


class ProjectPage(rio.Component):
    project: rio.cli.project.RioProject | None = None

    def __post_init__(self) -> None:
        self.project = rio.cli.project.RioProject.try_load()

    async def _on_change_app_type(self, event: rio.DropdownChangeEvent) -> None:
        assert self.project is not None
        self.project.app_type = event.value
        self.project.write()
        await self.force_refresh()

    def build(self) -> rio.Component:
        # No project
        if self.project is None:
            return rio.Column(
                rio.Icon("error", width=4, height=4, fill="danger"),
                rio.Text(
                    "Couldn't find your project files. Do you have a `rio.toml` file?",
                    multiline=True,
                ),
            )

        # Project
        project_name = self.project.project_directory.name.strip().capitalize()

        return rio.Column(
            rio.Text(
                project_name,
                style="heading2",
                align_x=0,
            ),
            rio.Text(
                str(self.project.project_directory),
                style="dim",
                margin_bottom=2,
                align_x=0,
            ),
            rio.Text(
                "To launch your project, Rio needs to know the name of your python module and in which variable you've stored your app. You can configure those here",
                multiline=True,
            ),
            rio.TextInput(
                label="Main Module",
            ),
            rio.TextInput(
                label="App Variable",
            ),
            rio.Text(
                "Rio can create both apps and websites. Apps will launch in a separate window, while websites will launch in your browser. Which type is your project?",
                multiline=True,
            ),
            rio.Dropdown(
                label="Type",
                options={
                    "App": "app",
                    "Website": "website",
                },
            ),
            margin=1,
            align_y=0,
        )
