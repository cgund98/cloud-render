"""
UI components for creating new render jobs.
"""
from bpy.types import Panel, Operator, PropertyGroup
from bpy.props import BoolProperty, PointerProperty
import bpy

from cloud_render.creds import valid_creds
from ..init import init_jobs_controller
from ..base import CloudRender_BasePanel

class CloudRender_CloudCreateJobProps(PropertyGroup):
    """Properties for credentials inputs"""

    animation: BoolProperty(name="Render Animation", description="If true, render entire animation. Otherwise, render the current frame.")

class CloudRender_OT_CreateJob(Operator):
    """Operator that will create a new render job."""

    bl_idname = "render.create_cloud_render_job"
    bl_label = "Create Job"
    bl_description = "Pack resources and upload blend file to the cloud"

    @classmethod
    def poll(cls, _):
        """Validate operator conditions."""
        return valid_creds() and bpy.data.filepath

    def execute(self, context):
        """Execute the operator."""

        # Initialize jobs manager
        jobs_controller = init_jobs_controller()

        scene = context.scene

        # Pack resources
        bpy.ops.file.pack_all()
        file_path = bpy.data.filepath

        # Save file
        bpy.ops.wm.save_mainfile()

        # Set start and end frames
        props = scene.CloudCreateJobProps
        if props.animation:
            start_frame, end_frame = scene.frame_start, scene.frame_end

        if not props.animation:
            start_frame, end_frame = scene.frame_current, scene.frame_current

        # Create the job (GPU disabled for now)
        jobs_controller.create_job(file_path, start_frame, end_frame)

        if start_frame == end_frame:
            self.report({"INFO"}, f"Created render job for single frame #{start_frame}")
        else:
            self.report({'INFO'}, f"Created render job for frames #{start_frame} to #{end_frame}")

        return {'FINISHED'}

    def invoke(self, context, event):
        """Add a confirmation dialog"""

        return context.window_manager.invoke_confirm(self, event)


class CloudRender_PT_NewJobPanel(CloudRender_BasePanel, Panel):
    """Subpanel that shows current jobs"""

    bl_parent_id = "cloud_render_jobs_panel"
    bl_label = "New"

    def draw(self, context):
        """Render UI components"""

        # Ensure creds are set
        if not valid_creds():
            return

        scene = context.scene

        # Form inputs
        split = self.layout.split(factor=0.5)
        labels_col = split.column()
        labels_col.alignment = 'RIGHT'
        labels_col.label(text="Render Animation")
        
        props = bpy.context.scene.CloudCreateJobProps
        inputs_col = split.column()
        inputs_col.prop(props, "animation", text="")

        row = self.layout.row()
        row.operator(CloudRender_OT_CreateJob.bl_idname, text="Create job")

        



classes = (
    CloudRender_PT_NewJobPanel,
    CloudRender_OT_CreateJob,
    CloudRender_CloudCreateJobProps,
)

def register():
    """Register blender UI components"""

    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.CloudCreateJobProps = PointerProperty(type=CloudRender_CloudCreateJobProps)


def unregister():
    """Unregister blender UI components"""

    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.CloudCreateJobProps
