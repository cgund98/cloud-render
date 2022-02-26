"""
UI components for managing existing render jobs.
"""
from bpy.types import PropertyGroup, Panel, UIList, Operator
from bpy.props import StringProperty, CollectionProperty, IntProperty
import bpy

from cloud_render.creds import valid_creds
from ..init import init_jobs_controller
from ..base import CloudRender_BasePanel


class CloudRender_OT_RefreshJobs(Operator):
    bl_idname = "render.refresh_cloud_jobs"
    bl_label = "Refresh"
    bl_description = "Refresh the list of current available jobs"
    
    @classmethod
    def poll(cls, _):
        return valid_creds()

    def execute(self, context):
        """Execute the operator."""
        # Init the jobs controller
        jobs_controller = init_jobs_controller()

        # Fetch active jobs
        jobs = jobs_controller.list_jobs()
        
        # Populate jobs list
        context.scene.jobs_list.clear()
        for job in jobs:
            item = context.scene.jobs_list.add()
            item.name = job.job_id
            item.status = job.status
            item.file_name = job.file_name
        
        self.report({'INFO'}, f"Refreshed jobs status.")

        return {'FINISHED'}


class CloudRender_PT_ManageJobsPanel(CloudRender_BasePanel, Panel):
    """Subpanel that shows current jobs"""

    bl_parent_id = "cloud_render_jobs_panel"
    bl_label = "Manage"

    def draw(self, context):
        """Render UI components"""

        # Ensure creds are set
        if not valid_creds():
            return

        scene = context.scene

        row = self.layout.row()
        row.template_list("CloudRender_UL_JobList", "JobList", scene, "jobs_list", scene, "jobs_index")

        row = self.layout.row()
        row = self.layout.row()
        split = self.layout.split(factor=0.5)

        col = split.column()
        col.operator(CloudRender_OT_RefreshJobs.bl_idname, text="Refresh", icon="FILE_REFRESH")

class CloudRender_JobListItem(PropertyGroup):
    """Group of properties representing a job in the list."""

    name: StringProperty(name="name", description="Job name")
    status: StringProperty(name="status", description="Job status")
    file_name: StringProperty(name="filename", description="Blend file name")


class CloudRender_UL_JobList(UIList):
    """Jobs list"""

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        """Render list item"""

        # Use a custom icon
        icon = 'REC'
        if item.status == "SUCCEEDED":
            icon = 'CHECKMARK'
        elif item.status == "FAILED":
            icon = 'ORPHAN_DATA'

        # List text
        text = f"{item.name} ({item.file_name})"

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=text, icon=icon)

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text=text, icon=icon)


classes = (
    CloudRender_OT_RefreshJobs,
    CloudRender_PT_ManageJobsPanel,
    CloudRender_JobListItem,
    CloudRender_UL_JobList
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