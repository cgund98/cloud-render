"""
Blender UI components related to saving AWS credentials
"""
from bpy.types import Operator, Panel
from bpy.props import StringProperty
import bpy

from ..creds import valid_creds
from .init import init_stack_manager
from .base import CloudRender_BasePanel

# Constants
NOT_DEPLOYED = "NOT_DEPLOYED"
DELETE_IN_PROGRESS = "DELETE_IN_PROGRESS"
CREATE_COMPLETE = "CREATE_COMPLETE"
UPDATE_COMPLETE = "UPDATE_COMPLETE"
READY = "READY"
UNKNOWN = "UNKNOWN"


class CloudRender_OT_DeployFarm(Operator):
    """Operator that will deploy a new render farm."""

    bl_idname = "render.deploy_render_farm"
    bl_label = "Deploy"
    bl_description = "Deploy a new render farm on AWS."

    @classmethod
    def poll(cls, _):
        """Validate operator conditions."""
        return valid_creds()

    def execute(self, _):
        """Execute the operator."""
        stack_manager = init_stack_manager()

        stack_manager.create_or_update()

        self.report({"INFO"}, "Deployed render farm.")

        bpy.ops.render.refresh_render_farm_status()

        return {"FINISHED"}


class CloudRender_OT_DeleteFarm(Operator):
    """Operator that will shut down the render farm."""

    bl_idname = "render.delete_render_farm"
    bl_label = "Shut Down"
    bl_description = "Shut down the active render farm."

    @classmethod
    def poll(cls, _):
        """Validate operator conditions."""
        return valid_creds()

    def execute(self, _):
        """Execute the operator."""
        stack_manager = init_stack_manager()

        stack_manager.delete()

        self.report({"INFO"}, "Deleted render farm. Please wait for resources to be removed.")

        bpy.ops.render.refresh_render_farm_status()

        return {"FINISHED"}

    def invoke(self, context, event):
        """Add a confirmation dialog"""

        return context.window_manager.invoke_confirm(self, event)


class CloudRender_OT_RefreshFarmStatus(Operator):
    """Operator that will refresh the status of the render farm."""

    bl_idname = "render.refresh_render_farm_status"
    bl_label = "Refresh"
    bl_description = "Refresh the status of the current deployed render farm."

    @classmethod
    def poll(cls, _):
        """Validate operator conditions."""
        return valid_creds()

    def execute(self, context):
        """Execute the operator."""
        stack_manager = init_stack_manager()

        stack = stack_manager.get()
        if stack is None:
            context.scene.farm_status = NOT_DEPLOYED
        else:
            context.scene.farm_status = stack.status

        self.report({"INFO"}, "Refreshed render farm status.")

        return {"FINISHED"}


class CloudRender_PT_RenderFarmPanel(CloudRender_BasePanel, Panel):
    """Subpanel that shows options for authenticating to AWS"""

    bl_parent_id = "cloud_render_primary_panel"
    bl_label = "Render Farm"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        """Render UI components"""

        row = self.layout.row()
        row.label(text="Check the status of, deploy, or shut down you render farm.")

        # Check if credentials are set
        if not valid_creds():
            row = self.layout.row()
            row.label(text="Save AWS credentials to view.")
            return

        # Read render farm status
        status = context.scene.farm_status
        if status in (CREATE_COMPLETE, UPDATE_COMPLETE):
            status = READY
        elif status == "":
            status = UNKNOWN

        # Status label
        row = self.layout.row()
        row.label(text=f"Farm Status: {status}")

        # Operators
        row = self.layout.row()
        split = self.layout.split(factor=0.5)

        col = split.column()
        col.operator(
            CloudRender_OT_RefreshFarmStatus.bl_idname,
            text="Refresh",
            icon="FILE_REFRESH",
        )

        col = split.column()
        if status == UNKNOWN:
            return
        if status == NOT_DEPLOYED:
            col.operator(CloudRender_OT_DeployFarm.bl_idname, icon="ADD")
        elif status != DELETE_IN_PROGRESS:
            col.operator(CloudRender_OT_DeleteFarm.bl_idname, icon="X")


classes = (
    CloudRender_OT_DeployFarm,
    CloudRender_OT_DeleteFarm,
    CloudRender_OT_RefreshFarmStatus,
    CloudRender_PT_RenderFarmPanel,
)


def register():
    """Register blender UI components"""

    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.farm_status = StringProperty(name="Farm Status")


def unregister():
    """Unregister blender UI components"""

    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.farm_status
