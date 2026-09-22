"""
Jeweler 3D Studio - Viewport Add Menu Integration (Shift + A)
Appends Jeweler 3D Studio creation operators to:
  - Add > Curve (VIEW3D_MT_curve_add)
  - Add > Mesh (VIEW3D_MT_mesh_add)
  - Add > Jeweler 3D (VIEW3D_MT_add submenu)
"""

import bpy
from bpy.types import Menu


class VIEW3D_MT_j3d_add_menu(Menu):
    """Dedicated submenu in Shift + A > Jeweler 3D"""
    bl_idname = "VIEW3D_MT_j3d_add_menu"
    bl_label = "Jeweler 3D"

    def draw(self, context: bpy.types.Context) -> None:
        layout = self.layout

        # Rings & Sizes section
        layout.label(text="Rings & Sizes", icon='MESH_TORUS')
        op_curve = layout.operator("j3d_community.create_ring_size", text="Ring Size (Curve)", icon='CURVE_NCIRCLE')
        op_curve.geometry_type = 'CURVE'

        op_mesh = layout.operator("j3d_community.create_ring_size", text="Ring Size (Cylinder)", icon='MESH_CYLINDER')
        op_mesh.geometry_type = 'CYLINDER'

        layout.operator("j3d_community.create_ring_profile", text="Ring Shank (Profile)", icon='MESH_TORUS')

        layout.separator()

        # Gems section
        layout.label(text="Gems", icon='MESH_ICOSPHERE')
        layout.operator("j3d_community.add_gem", text="Add Gem", icon='MESH_ICOSPHERE')


def menu_func_curve(self, context: bpy.types.Context) -> None:
    """Entry in Shift + A > Curve"""
    layout = self.layout
    layout.separator()
    op = layout.operator("j3d_community.create_ring_size", text="Ring Size (Curve)", icon='CURVE_NCIRCLE')
    op.geometry_type = 'CURVE'


def menu_func_mesh(self, context: bpy.types.Context) -> None:
    """Entry in Shift + A > Mesh"""
    layout = self.layout
    layout.separator()
    op = layout.operator("j3d_community.create_ring_size", text="Ring Size (Cylinder)", icon='MESH_CYLINDER')
    op.geometry_type = 'CYLINDER'
    layout.operator("j3d_community.create_ring_profile", text="Ring Shank (Profile)", icon='MESH_TORUS')


def menu_func_add_top(self, context: bpy.types.Context) -> None:
    """Submenu entry in root of Shift + A"""
    layout = self.layout
    layout.separator()
    layout.menu(VIEW3D_MT_j3d_add_menu.bl_idname, text="Jeweler 3D", icon='MESH_ICOSPHERE')


classes = (
    VIEW3D_MT_j3d_add_menu,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.VIEW3D_MT_curve_add.append(menu_func_curve)
    bpy.types.VIEW3D_MT_mesh_add.append(menu_func_mesh)
    bpy.types.VIEW3D_MT_add.append(menu_func_add_top)


def unregister():
    try:
        bpy.types.VIEW3D_MT_add.remove(menu_func_add_top)
    except Exception:
        pass
    try:
        bpy.types.VIEW3D_MT_mesh_add.remove(menu_func_mesh)
    except Exception:
        pass
    try:
        bpy.types.VIEW3D_MT_curve_add.remove(menu_func_curve)
    except Exception:
        pass
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except Exception:
            pass
