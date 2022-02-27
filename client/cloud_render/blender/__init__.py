"""
Blender user interfaces are defined here.
"""
from bpy.types import Panel
import bpy

from . import jobs, render_farm, creds, base


class CloudRender_PT_PrimaryPanel(base.CloudRender_BasePanel, Panel):
    """Primary panel in the Render settings section of the Properties space"""

    bl_idname = "cloud_render_primary_panel"
    bl_label = "Cloud Render"

    def draw(self, context):
        """Render UI components"""


blender_classes = (CloudRender_PT_PrimaryPanel,)


def register_elements():
    """Register UI elements"""

    for cls in blender_classes:
        bpy.utils.register_class(cls)

    # Unregister child components
    creds.register()
    render_farm.register()
    jobs.register()


def unregister_elements():
    """Unregister UI elements"""

    for cls in blender_classes:
        bpy.utils.unregister_class(cls)

    creds.unregister()
    render_farm.unregister()
    jobs.unregister()
