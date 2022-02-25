"""
Blender UI components related to saving AWS credentials
"""
from bpy.types import PropertyGroup, Operator, Panel
from bpy.props import StringProperty, PointerProperty
import bpy

from cloud_render.creds import save_creds, load_creds, valid_creds
from .base import CloudRender_BasePanel

class CloudRender_DeployFarm(Operator):
    bl_idname = "render.deploy_render_farm"
    bl_label = "Deploy"
    bl_description = "Deploy a new render farm on AWS."

    @classmethod
    def poll(cls, context):
        return valid_creds

    def execute(self, context):
        cur_creds = load_creds()
        self.report({'INFO'}, f"Deployed render farm.")

        return {'FINISHED'}

class CloudRender_RefreshFarmStatus(Operator):
    bl_idname = "render.refresh_render_farm_status"
    bl_label = "Refresh"
    bl_description = "Refresh the status of the current deployed render farm."

    def execute(self, context):
        cur_creds = load_creds()
        self.report({'INFO'}, f"Refreshed render farm status.")

        return {'FINISHED'}

class CloudRender_RenderFarmPanel(CloudRender_BasePanel, Panel):
    """Subpanel that shows options for authenticating to AWS"""

    bl_parent_id = "cloud_render_primary_panel"
    bl_label = "Render Farm"
    bl_options = {"HEADER_LAYOUT_EXPAND"}

    def draw(self, context):
        """Render UI components"""

        # Check if credentials are set
        if not valid_creds():
            self.layout.row().label(text="Save AWS credentials to view.")
            return

        row = self.layout.row()
        row.operator(CloudRender_RefreshFarmStatus.bl_idname, text="Refresh")


classes = (
    CloudRender_DeployFarm,
    CloudRender_RefreshFarmStatus,
    CloudRender_RenderFarmPanel,
)

def register():
    """Register blender UI components"""

    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    """Unregister blender UI components"""

    for cls in classes:
        bpy.utils.unregister_class(cls)
