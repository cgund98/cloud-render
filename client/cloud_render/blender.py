"""
Blender user interfaces are defined here.
"""
import bpy

from cloud_render.creds import save_creds, load_creds, valid_creds


class CloudRender_CloudCredsProps(bpy.types.PropertyGroup):

    access_key_id: bpy.props.StringProperty(name="Access Key ID")
    secret_access_key: bpy.props.StringProperty(name="Secret Access Key")


class CloudRender_SetCredentials(bpy.types.Operator):
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


class CloudRender_BasePanel:
    """Base class for base panels"""

    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"

class CloudRender_PrimaryPanel(CloudRender_BasePanel, bpy.types.Panel):
    """Primary panel in the Render settings section of the Properties space"""

    bl_label = "Cloud Render"

    def draw(self, context):
        """Render UI components"""

        layout = self.layout

        lines = [f"What's up bro",]

        for line in lines:
            layout.label(text=line)


class CloudRender_CredentialsPanel(CloudRender_BasePanel, bpy.types.Panel):
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


blender_classes = (
    CloudRender_CloudCredsProps,
    CloudRender_SetCredentials,
    CloudRender_PrimaryPanel,
    CloudRender_CredentialsPanel,
)


def register_elements():
    """Register UI elements"""

    for cls in blender_classes:
        bpy.utils.register_class(cls)

    # Register CloudCredsProps
    bpy.types.Scene.CloudCredsProps = bpy.props.PointerProperty(type=CloudRender_CloudCredsProps)


def unregister_elements():
    """Unregister UI elements"""

    for cls in blender_classes:
        bpy.utils.unregister_class(cls)

    # Unregister CloudCredsProps
    del(bpy.types.Scene.CloudCredsProps)