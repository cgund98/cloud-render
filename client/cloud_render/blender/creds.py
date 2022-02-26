"""
Blender UI components related to saving AWS credentials
"""
from bpy.types import PropertyGroup, Operator, Panel
from bpy.props import StringProperty, PointerProperty
import bpy

from cloud_render.creds import save_creds, valid_creds
from .base import CloudRender_BasePanel

class CloudRender_CloudCredsProps(PropertyGroup):
    """Properties for credentials inputs"""

    region: StringProperty(name="AWS Region")
    access_key_id: StringProperty(name="Access Key ID")
    secret_access_key: StringProperty(name="Secret Access Key")


class CloudRender_SetCredentials(Operator):
    bl_idname = "render.set_aws_credentials"
    bl_label = "Reset AWS Creds"
    bl_description = "Set or reset AWS credentials. Required for further cloud render steps."

    def execute(self, context):
        props = context.scene.CloudCredsProps

        if props.access_key_id == "" and props.secret_access_key == "":
            self.report({'INFO'}, f"Reset credentials.")
        else:
            self.report({'INFO'}, f"Saved credentials.")
        
        # Save to FS
        save_creds(props.access_key_id, props.secret_access_key, props.region)

        props.access_key_id = ""
        props.secret_access_key = ""

        return {'FINISHED'}

    def invoke(self, context, event):
        """If credentials are valid, add a confirmation to delete them"""

        if valid_creds():
            return context.window_manager.invoke_confirm(self, event)

        return self.execute(context)
        


class CloudRender_CredentialsPanel(CloudRender_BasePanel, Panel):
    """Subpanel that shows options for authenticating to AWS"""

    bl_parent_id = "cloud_render_primary_panel"
    bl_label = "AWS Credentials"
    bl_options = {"HEADER_LAYOUT_EXPAND"}

    def draw(self, context):
        """Render UI components"""

        # Check if credentials are set
        if not valid_creds():
            props = bpy.context.scene.CloudCredsProps

            row = self.layout.row()
            row.label(text="Please enter your AWS credentials.")

            inputs_row = self.layout.split(factor=0.3, align=True)
            labels_col = inputs_row.column()
            labels_col.alignment = 'RIGHT'
            labels_col.label(text="AWS Region")
            labels_col.label(text="Access Key ID")
            labels_col.label(text="Secret Access Key")

            inputs_col = inputs_row.column()
            inputs_col.prop(props, "region", text="")
            inputs_col.prop(props, "access_key_id", text="")
            inputs_col.prop(props, "secret_access_key", text="")

            row = self.layout.row()
            row.operator_context = 'INVOKE_DEFAULT'
            row.operator(CloudRender_SetCredentials.bl_idname, text="Set AWS Credentials")
        
        # Hide inputs otherwise
        else:
            row = self.layout.row()
            row.label(text="Credentials currently saved.")

            row = self.layout.row()
            row.operator(CloudRender_SetCredentials.bl_idname, text="Reset Credentials")
            row = self.layout.row()


classes = (
    CloudRender_CloudCredsProps,
    CloudRender_SetCredentials,
    CloudRender_CredentialsPanel,
)

def register():
    """Register blender UI components"""

    for cls in classes:
        bpy.utils.register_class(cls)

    # Register CloudCredsProps
    bpy.types.Scene.CloudCredsProps = PointerProperty(type=CloudRender_CloudCredsProps)


def unregister():
    """Unregister blender UI components"""

    for cls in classes:
        bpy.utils.unregister_class(cls)

    # Register CloudCredsProps
    del bpy.types.Scene.CloudCredsProps