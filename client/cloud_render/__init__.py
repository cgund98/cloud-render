"""
Entrypoint for blender add-on registration.

Big thanks to Robert Gützkow for the code on installing pip dependencies inside of blender.
See his example at https://github.com/robertguetzkow/blender-python-examples/tree/master/add_ons/install_dependencies.
"""

# pylint: disable=import-outside-toplevel

# The try-except block is to allow the CLI to work, even when
# being ran outside of blender.
try:
    import bpy
    import os
    import sys
    import subprocess
    import importlib
    from collections import namedtuple

    bl_info = {
        "name": "Cloud Render",
        "author": "Callum Gundlach",
        "version": (0, 1, 0),
        "blender": (3, 0, 1),
        "location": "Properties > Render Settings > Cloud Render",
        "description": "Add-on that launches your own render farm on AWS",
        "warning": "Requires installation of dependencies",
        "support": "COMMUNITY",
        "wiki_url": "https://github.com/cgund98/cloud-render",
        "tracker_url": "https://github.com/cgund98/cloud-render/issues",
        "category": "Render",
    }

    Dependency = namedtuple("Dependency", ["module", "package", "name"])

    dependencies = (
        Dependency(module="boto3", package=None, name=None),
        Dependency(module="mypy_boto3_s3", package="boto3-stubs[essential]", name=None),
        Dependency(module="mypy_boto3_batch", package="boto3-stubs[batch]", name=None),
        Dependency(module="pydantic", package=None, name=None),
        Dependency(module="typer", package=None, name=None),
    )

    DEPENDENCIES_INSTALLED = False

    def import_module(module_name, global_name=None):
        """
        Import a module.
        :param module_name: Module to import.
        :param global_name: (Optional) Name under which the module is imported. If None the module_name will be used.
        This allows to import under a different name with the same effect as e.g. "import numpy as np" where "np" is
        the global_name under which the module can be accessed.
        :raises: ImportError and ModuleNotFoundError
        """
        if global_name is None:
            global_name = module_name

        if global_name in globals():
            importlib.reload(globals()[global_name])
        else:
            # Attempt to import the module and assign it to globals dictionary. This allow to access the module under
            # the given name, just like the regular import would.
            globals()[global_name] = importlib.import_module(module_name)

    def install_pip():
        """
        Installs pip if not already present. Please note that ensurepip.bootstrap() also calls pip, which adds the
        environment variable PIP_REQ_TRACKER. After ensurepip.bootstrap() finishes execution, the directory doesn't
        exist anymore. However, when subprocess is used to call pip, in order to install a package, the environment
        variables still contain PIP_REQ_TRACKER with the now nonexistent path. This is a problem since pip checks if
        PIP_REQ_TRACKER is set and if it is, attempts to use it as temp directory. This would result in an error
        because the directory can't be found. Therefore, PIP_REQ_TRACKER needs to be removed from environment vars.
        :return:
        """

        try:
            # Check if pip is already installed
            subprocess.run([sys.executable, "-m", "pip", "--version"], check=True)
        except subprocess.CalledProcessError:
            import ensurepip

            ensurepip.bootstrap()
            os.environ.pop("PIP_REQ_TRACKER", None)

    def install_and_import_module(module_name, package_name=None, global_name=None):
        """
        Installs the package through pip and attempts to import the installed module.
        :param module_name: Module to import.
        :param package_name: (Optional) Name of the package that needs to be installed. If None it is assumed to be
        equal to the module_name.
        :param global_name: (Optional) Name under which the module is imported. If None the module_name will be used.
        This allows to import under a different name with the same effect as e.g. "import numpy as np" where "np" is
        the global_name under which the module can be accessed.
        :raises: subprocess.CalledProcessError and ImportError
        """
        if package_name is None:
            package_name = module_name

        if global_name is None:
            global_name = module_name

        # Blender disables the loading of user site-packages by default. However, pip will still check them to
        # determine if a dependency is already installed. This can cause problems if the packages is installed in the
        # user site-packages and pip deems the requirement satisfied, but Blender cannot import the package from the
        # user site-packages. Hence, the environment variable PYTHONNOUSERSITE is set to disallow pip from checking
        # the user site-packages. If the package is not already installed for Blender's Python interpreter, it will
        # then try to. The paths used by pip can be checked with
        # `subprocess.run([bpy.app.binary_path_python, "-m", "site"], check=True)`.

        # Create a copy of the environment variables and modify them for the subprocess call
        environ_copy = dict(os.environ)
        environ_copy["PYTHONNOUSERSITE"] = "1"

        subprocess.run(
            [sys.executable, "-m", "pip", "install", package_name],
            check=True,
            env=environ_copy,
        )

        # The installation succeeded, attempt to import the module again
        import_module(module_name, global_name)

    class InstallDependenciesOperator(bpy.types.Operator):
        """Button in the settings menu to install pip dependencies."""

        bl_idname = "cloud_render.install_dependencies"
        bl_label = "Install dependencies"
        bl_description = (
            "Downloads and installs the required python packages for this add-on. "
            "Internet connection is required. Blender may have to be started with "
            "elevated permissions in order to install the package"
        )
        bl_options = {"REGISTER", "INTERNAL"}

        @classmethod
        def poll(cls, _):
            """
            Check if required conditions have been met.

            Deactivate when dependencies have been installed.
            """

            return not DEPENDENCIES_INSTALLED

        def execute(self, _):
            """Execute the operator."""
            try:
                install_pip()
                for dependency in dependencies:
                    install_and_import_module(
                        module_name=dependency.module,
                        package_name=dependency.package,
                        global_name=dependency.name,
                    )
            except (subprocess.CalledProcessError, ImportError) as err:
                self.report({"ERROR"}, str(err))
                return {"CANCELLED"}

            global DEPENDENCIES_INSTALLED
            DEPENDENCIES_INSTALLED = True

            # Register the panels, operators, etc. since dependencies are installed
            from .blender import register_elements

            register_elements()

            return {"FINISHED"}

    class Preferences(bpy.types.AddonPreferences):
        """Preferences panel, holds the install dependencies button"""

        bl_idname = __name__

        def draw(self, _):
            """Render UI components."""
            layout = self.layout
            layout.operator(InstallDependenciesOperator.bl_idname, icon="CONSOLE")

    def register():
        """Register the add-on with blender"""

        global DEPENDENCIES_INSTALLED
        DEPENDENCIES_INSTALLED = False

        # Register preferences elements
        bpy.utils.register_class(Preferences)
        bpy.utils.register_class(InstallDependenciesOperator)

        # Check if dependencies are installed
        try:
            for dependency in dependencies:
                import_module(module_name=dependency.module, global_name=dependency.name)
            DEPENDENCIES_INSTALLED = True

        except ModuleNotFoundError:
            # Don't register other panels, operators etc.
            return

        # Register other elements
        from .blender import register_elements

        register_elements()

    def unregister():
        """Remove the add-on from blender"""

        # Unregister preferences elements
        bpy.utils.unregister_class(Preferences)
        bpy.utils.unregister_class(InstallDependenciesOperator)

        # Unregister other elements
        if DEPENDENCIES_INSTALLED:
            from .blender import unregister_elements

            unregister_elements()

except ModuleNotFoundError as error:
    if __name__ == "__main__":
        raise error


if __name__ == "__main__":
    register()
