"""
UI components for managing existing render jobs.
"""
from typing import Optional

from bpy.types import PropertyGroup, Panel, UIList, Operator
from bpy.props import StringProperty, CollectionProperty, IntProperty
import bpy

from cloud_render.creds import valid_creds
from cloud_render.config import STATUS_ERROR, STATUS_RUNNING, STATUS_SUCCEEDED
from cloud_render.jobs import Job
from ..init import init_jobs_controller
from ..base import CloudRender_BasePanel

last_id: Optional[str] = None
cur_job: Optional[Job] = None

def job_handler(self, context):
    """Handle changes to the active job"""
    global cur_job
    scene = context.scene

    # Ensure there is a selected job
    if not scene.jobs_index >= 0 or not scene.jobs_list:
        return

    cur_item = scene.jobs_list[scene.jobs_index]

    # Update current job if selected job changes
    if cur_item.id != last_id:
        jobs_controller = init_jobs_controller()

        cur_job = jobs_controller.get_job(cur_item.id)


class CloudRender_OT_DeleteJob(Operator):
    """Operator that will delete the selected cloud render job."""

    bl_idname = "render.delete_cloud_job"
    bl_label = "Delete"
    bl_description = "Cancel/delete selected render job."
    
    @classmethod
    def poll(cls, context):
        scene = context.scene

        return valid_creds() and scene.jobs_index >= 0 and scene.jobs_list

    def execute(self, context):
        """Execute the operator."""
        scene = context.scene

        # Init the jobs controller
        jobs_controller = init_jobs_controller()

        # Fetch active jobs
        jobs = jobs_controller.list_jobs()

        # Set id of current job, so we can set list index to same job after resetting list
        active_job = scene.jobs_list[scene.jobs_index]

        # Check that current job exists
        job = jobs_controller.get_job(active_job.id)
        if job is None:
            return {'ERROR'}

        # Delete job
        jobs_controller.delete_job(job)

        # Refresh jobs
        bpy.ops.render.refresh_cloud_jobs()
        
        self.report({'INFO'}, f"Deleted selected job.")

        return {'FINISHED'}

    def invoke(self, context, event):
        """Add a confirmation dialog"""

        return context.window_manager.invoke_confirm(self, event)


class CloudRender_OT_RefreshJobs(Operator):
    """Operator that will refresh the list of active cloud render jobs."""

    bl_idname = "render.refresh_cloud_jobs"
    bl_label = "Refresh"
    bl_description = "Refresh the list of current available jobs"
    
    @classmethod
    def poll(cls, _):
        return valid_creds()

    def execute(self, context):
        """Execute the operator."""
        scene = context.scene

        # Init the jobs controller
        jobs_controller = init_jobs_controller()

        # Fetch active jobs
        jobs = jobs_controller.list_jobs()

        # Set id of current job, so we can set list index to same job after resetting list
        cur_job_id, new_index = None, 0
        if scene.jobs_index >= 0 and scene.jobs_list:
            cur_job_id = scene.jobs_list[scene.jobs_index].id
        
        # Populate jobs list
        context.scene.jobs_list.clear()
        for i, job in enumerate(jobs):
            item = scene.jobs_list.add()
            item.id = job.job_id
            item.status = job.status
            item.file_name = job.file_name

            # Update list index
            if job.job_id == cur_job_id:
                new_index = i

        scene.jobs_index = new_index

        job_handler(self, context)
        
        self.report({'INFO'}, f"Refreshed jobs status.")

        return {'FINISHED'}


class CloudRender_PT_ManageJobsPanel(CloudRender_BasePanel, Panel):
    """Subpanel that shows current jobs"""

    bl_parent_id = "cloud_render_jobs_panel"
    bl_label = "Manage"

    def draw(self, context):
        """Render UI components"""

        global cur_job

        # Ensure creds are set
        if not valid_creds():
            return

        scene = context.scene

        self.layout.row().label(text="Existing Jobs:")
        row = self.layout.row()
        row.template_list("CloudRender_UL_JobList", "JobList", scene, "jobs_list", scene, "jobs_index")

        # Jobs list buttons
        row = self.layout.row()
        split = self.layout.split(factor=0.5)

        col = split.column()
        col.operator(CloudRender_OT_RefreshJobs.bl_idname, text="Refresh", icon="FILE_REFRESH")

        col = split.column()
        col.operator(CloudRender_OT_DeleteJob.bl_idname, text="Delete Job", icon="TRASH")

        # Job Details
        if scene.jobs_index >= 0 and scene.jobs_list:

            # Ensure we have a current job fetched from backend
            if not cur_job:
                return

            split = self.layout.row().split(factor=0.5)
            labels_col = split.column()
            labels_col.alignment = "RIGHT"
            values_col = split.column()

            # Job metadata
            labels_col.label(text="Job ID:")
            values_col.label(text=cur_job.job_id)

            labels_col.label(text="Blend file:")
            values_col.label(text=cur_job.file_name)

            labels_col.label(text="Job Status:")
            values_col.label(text=cur_job.status)

            # Calculate frame stats
            finished_frames = 0
            failed_frames = 0
            running_frames = 0
            total_frames = cur_job.end_frame - cur_job.start_frame + 1

            for batch_job in cur_job.children.values():
                if batch_job.status == "RUNNING":
                    running_frames += 1
                elif batch_job.status == "SUCCEEDED":
                    finished_frames += 1
                elif batch_job.status == "FAILED":
                    failed_frames += 1

            labels_col.label(text="Completed Frames:")
            values_col.label(text=f"{finished_frames}/{total_frames}")
            
            labels_col.label(text="Failed Frames:")
            values_col.label(text=f"{failed_frames}/{total_frames}")

            labels_col.label(text="Running Frames:")
            values_col.label(text=f"{running_frames}")


class CloudRender_JobListItem(PropertyGroup):
    """Group of properties representing a job in the list."""

    id: StringProperty(name="id", description="Job id")
    status: StringProperty(name="status", description="Job status")
    file_name: StringProperty(name="filename", description="Blend file name")


class CloudRender_UL_JobList(UIList):
    """Jobs list"""

    def draw_item(self, _, layout, __, item, icon, ___, ____, _____):
        """Render list item"""

        # Use a custom icon
        icon = 'REC'
        if item.status == STATUS_SUCCEEDED:
            icon = 'CHECKMARK'
        elif item.status == STATUS_ERROR:
            icon = 'ORPHAN_DATA'

        # List text
        text = f"{item.id} ({item.file_name})"

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=text, icon=icon)

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text=text, icon=icon)


classes = (
    CloudRender_OT_DeleteJob,
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
    bpy.types.Scene.jobs_index = IntProperty(name="Index for jobs_list", default=0, update=job_handler)


def unregister():
    """Unregister blender UI components"""

    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.jobs_list
    del bpy.types.Scene.jobs_index