"""
Blender UI components pertaining to render jobs
"""
from bpy.types import PropertyGroup, Panel, UIList
from bpy.props import StringProperty, CollectionProperty, IntProperty
import bpy

from .base import CloudRender_BasePanel

class CloudRender_JobsPanel(CloudRender_BasePanel, Panel):
    """Subpanel that shows current jobs"""

    bl_parent_id = "cloud_render_primary_panel"
    bl_label = "Jobs"

    def draw(self, context):
        """Render UI components"""

        scene = context.scene

        row = self.layout.row()
        row.template_list("CloudRender_JobList", "JobList", scene, "jobs_list", scene, "jobs_index")


class CloudRender_JobListItem(PropertyGroup):
    """Group of properties representing a job in the list."""

    name: StringProperty(name="name", description="Job name")


class CloudRender_JobList(UIList):
    """Jobs list"""

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        """Render list item"""

        # Use a custom icon
        custom_icon = 'REC'

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=item.name, icon=custom_icon)

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon=custom_icon)


classes = (
    CloudRender_JobsPanel,
    CloudRender_JobListItem,
    CloudRender_JobList
)

def register():
    """Register blender UI components"""

    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.jobs_list = CollectionProperty(type=CloudRender_JobListItem)
    bpy.types.Scene.jobs_index = IntProperty(name="Index for jobs_list", default=0)


def unregister():
    """Unregister blender UI components"""

    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.jobs_list
    del bpy.types.Scene.jobs_index