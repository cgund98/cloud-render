"""
Blender UI components related to saving AWS credentials
"""
from bpy.types import PropertyGroup, Operator, Panel
from bpy.props import StringProperty, PointerProperty
import bpy

from cloud_render.creds import save_creds, load_creds, valid_creds
from .base import CloudRender_BasePanel

class CloudRender_CloudCredsProps(PropertyGroup):
    """Properties for credentials inputs"""

    access_key_id: StringProperty(name="Access Key ID")
    secret_access_key: StringProperty(name="Secret Access Key")


def set_job_enum(self, value: str) -> None:
    print(value)
    return None

class CloudRender_SetCredentials(Operator):
    bl_idname = "render.set_aws_credentials"
    bl_label = "Register AWS Creds"

    def execute(self, context):
        cur_creds = load_creds()
        self.report({'INFO'}, f"Saved credentials.")

        props = bpy.context.scene.CloudCredsProps
        
        # Save to FS
        save_creds(props.access_key_id, props.secret_access_key)

        props.access_key_id = ""
        props.secret_access_key = ""

        return {'FINISHED'}

class CloudRender_CredentialsPanel(CloudRender_BasePanel, Panel):
    """Subpanel that shows options for authenticating to AWS"""

    bl_parent_id = "CloudRender_PrimaryPanel"
    bl_label = "AWS Credentials"
    bl_options = {"HEADER_LAYOUT_EXPAND"}

    def draw(self, context):
        """Render UI components"""

        # Check if credentials are set
        if not valid_creds():
            props = bpy.context.scene.CloudCredsProps
            key_id_row = self.layout.row()
            key_id_row.prop(props, "access_key_id", text="Access Key ID")

            secret_key_row = self.layout.row()
            secret_key_row.prop(props, "secret_access_key", text="Secret Access Key")

            row = self.layout.row()
            row.operator(CloudRender_SetCredentials.bl_idname, text="Set AWS Credentials")
        
        # Hide inputs otherwise
        else:
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