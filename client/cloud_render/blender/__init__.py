"""
Blender user interfaces are defined here.
"""
from bpy.types import Panel
import bpy

from . import jobs, creds, base


class CloudRender_PrimaryPanel(base.CloudRender_BasePanel, Panel):
    """Primary panel in the Render settings section of the Properties space"""

    bl_label = "Cloud Render"

    def draw(self, context):
        """Render UI components"""

        layout = self.layout

        lines = [f"What's up bro",]

        for line in lines:
            layout.label(text=line)


blender_classes = (
    CloudRender_PrimaryPanel,
)


def register_elements():
    """Register UI elements"""

    for cls in blender_classes:
        bpy.utils.register_class(cls)

    # Register child components
    creds.register()
    jobs.register()


def unregister_elements():
    """Unregister UI elements"""

    for cls in blender_classes:
        bpy.utils.unregister_class(cls)

    # Unregister CloudCredsProps
    del bpy.types.Scene.CloudCredsProps