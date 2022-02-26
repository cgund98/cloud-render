"""
Blender UI components pertaining to render jobs
"""
from bpy.types import Panel
import bpy

from ..base import CloudRender_BasePanel
from . import manage, new

class CloudRender_PT_JobsPanel(CloudRender_BasePanel, Panel):
    """Subpanel that shows current jobs"""

    bl_parent_id = "cloud_render_primary_panel"
    bl_idname = "cloud_render_jobs_panel"
    bl_label = "Jobs"

    def draw(self, context):
        """Render UI components"""


classes = (
    CloudRender_PT_JobsPanel,
)

def register():
    """Register blender UI components"""

    for cls in classes:
        bpy.utils.register_class(cls)

    # Register children
    new.register()
    manage.register()


def unregister():
    """Unregister blender UI components"""

    for cls in classes:
        bpy.utils.unregister_class(cls)

    # Unregister children
    new.unregister()
    manage.unregister()