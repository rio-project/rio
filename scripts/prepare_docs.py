from revel import *  # type: ignore

import rio
import rio_docs


def main() -> None:
    # Find all classes that should be documented
    target_classes = [
        rio.App,
        rio.AssetError,
        rio.BoxStyle,
        rio.Color,
        rio.CursorStyle,
        rio.Font,
        rio.NavigationFailed,
        rio.Page,
        rio.Session,
        rio.TextStyle,
        rio.Theme,
        rio.UserSettings,
    ]

    # Add classes which should automatically have their children documented
    to_do = [
        rio.Fill,
        rio.Component,
    ]

    while to_do:
        cur = to_do.pop()
        target_classes.append(cur)
        to_do.extend(cur.__subclasses__())

    # Make sure they're all properly documented
    for cls in target_classes:
        # Fetch the docs
        docs = rio_docs.ClassDocs.parse(cls)

        # Postprocess them as needed
        if isinstance(cls, rio.Component):
            rio_docs.custom.postprocess_widget_docs(docs)
        else:
            rio_docs.custom.postprocess_class_docs(docs)

        # Run checks
        if docs.short_description is None:
            warning(f"Docstring for `{docs.name}` is missing a short description")

        if docs.long_description is None:
            warning(f"Docstring for `{docs.name}` is missing a long description")

        for attr in docs.attributes:
            if attr.description is None:
                warning(
                    f"Docstring for `{docs.name}.{attr.name}` is missing a description"
                )

        for func in docs.functions:
            if func.short_description is None:
                warning(
                    f"Docstring for `{docs.name}.{func.name}` is missing a short description"
                )

            if func.long_description is None:
                warning(
                    f"Docstring for `{docs.name}.{func.name}` is missing a long description"
                )


if __name__ == "__main__":
    main()
