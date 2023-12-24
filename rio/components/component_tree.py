from . import component_base


class ComponentTree(component_base.FundamentalComponent):
    """
    Note: This component makes not attempt to request the correct amount of
    space. Specify a width/height manually, or make sure it's in a properly
    sized parent.
    """

    pass


ComponentTree._unique_id = "ComponentTree-builtin"