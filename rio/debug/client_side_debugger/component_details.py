import rio


class ComponentDetails(rio.Component):
    def build(self) -> rio.Component:
        # Create a grid with all the details
        details_grid = rio.Grid(row_spacing=0.5, column_spacing=0.5)

        # TODO
        details_grid.add_child(rio.Text("TODO"), 0, 0)

        # Combine everything
        return rio.Column(
            rio.Text("Some component", style="heading3"),
            details_grid,
        )
