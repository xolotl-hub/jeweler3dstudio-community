"""
Jeweler 3D Studio - Galleries Operator
Procedural under-gallery generator (Wire, Knife, Milgrain).
Configured via Redo Panel (F9). Strictly kept < 250 lines.
"""

import bpy
from bpy.types import Operator, Context
from bpy.props import (
    EnumProperty,
    IntProperty,
    FloatProperty,
)
from mathutils import Vector, Matrix
from ..units import mm_to_bu
from ._geometry import (
    build_wire_gallery_bmesh,
    build_knife_gallery_bmesh,
    build_milgrain_gallery_bmesh,
)


GALLERY_ITEMS = [
    ('WIRE', 'Wire Gallery',
     'Tubular wire rails below the gem with vertical bridge connectors'),
    ('KNIFE', 'Knife Gallery',
     'Thin knife-edge wall with cutaway light windows'),
    ('MILGRAIN', 'Milgrain Gallery',
     'Decorative bead-edge wire rail below the gem seat'),
]


class J3DComm_OT_add_gallery(Operator):
    """Add parametric under-gallery structure to selected gemstone"""
    bl_idname = "j3d_community.add_gallery"
    bl_label = "Add Gallery"
    bl_description = (
        "Generates a parametric under-gallery (Wire, Knife, or Milgrain) "
        "for the active gemstone."
    )
    bl_options = {'REGISTER', 'UNDO'}

    style: EnumProperty(  # type: ignore
        name="Gallery Style",
        items=GALLERY_ITEMS,
        default='WIRE',
    )

    # Wire Gallery
    wire_r: FloatProperty(  # type: ignore
        name="Wire Radius", default=0.30, min=0.05, max=1.5, precision=2, subtype='DISTANCE'
    )
    n_rails: IntProperty(name="Rail Count", default=2, min=1, max=6)  # type: ignore
    rail_spacing: FloatProperty(  # type: ignore
        name="Rail Spacing", default=0.80, min=0.2, max=4.0, precision=2, subtype='DISTANCE'
    )
    n_bridges: IntProperty(name="Bridge Count", default=4, min=0, max=16)  # type: ignore
    bridge_r: FloatProperty(  # type: ignore
        name="Bridge Radius", default=0.22, min=0.05, max=1.0, precision=2, subtype='DISTANCE'
    )

    # Knife Gallery
    knife_wall: FloatProperty(  # type: ignore
        name="Wall Thickness", default=0.45, min=0.1, max=2.0, precision=2, subtype='DISTANCE'
    )
    knife_height: FloatProperty(  # type: ignore
        name="Gallery Height", default=1.20, min=0.3, max=5.0, precision=2, subtype='DISTANCE'
    )
    knife_windows: IntProperty(name="Window Count", default=4, min=0, max=16)  # type: ignore
    knife_arc: FloatProperty(  # type: ignore
        name="Window Arc (°)", default=35.0, min=5.0, max=80.0, precision=1
    )

    # Milgrain Gallery
    bead_r: FloatProperty(  # type: ignore
        name="Bead Radius", default=0.18, min=0.05, max=0.8, precision=2, subtype='DISTANCE'
    )
    n_beads: IntProperty(name="Bead Count", default=18, min=4, max=80)  # type: ignore
    milgrain_z: FloatProperty(  # type: ignore
        name="Z Offset", default=-0.60, min=-4.0, max=0.0, precision=2, subtype='DISTANCE'
    )
    milgrain_wire_r: FloatProperty(  # type: ignore
        name="Wire Radius", default=0.25, min=0.05, max=1.0, precision=2, subtype='DISTANCE'
    )

    def draw(self, context: Context) -> None:
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        layout.prop(self, "style", expand=False)

        if self.style == 'WIRE':
            box = layout.box()
            box.label(text="Wire Rails", icon='IPO_CIRC')
            box.prop(self, "wire_r")
            box.prop(self, "n_rails")
            box.prop(self, "rail_spacing")
            box2 = layout.box()
            box2.label(text="Bridge Connectors", icon='SNAP_VERTEX')
            box2.prop(self, "n_bridges")
            box2.prop(self, "bridge_r")

        elif self.style == 'KNIFE':
            box = layout.box()
            box.label(text="Knife Wall", icon='MOD_BEVEL')
            box.prop(self, "knife_wall")
            box.prop(self, "knife_height")
            box2 = layout.box()
            box2.label(text="Light Windows", icon='LIGHT_SUN')
            box2.prop(self, "knife_windows")
            box2.prop(self, "knife_arc")

        elif self.style == 'MILGRAIN':
            box = layout.box()
            box.label(text="Base Wire", icon='IPO_CIRC')
            box.prop(self, "milgrain_wire_r")
            box.prop(self, "milgrain_z")
            box2 = layout.box()
            box2.label(text="Bead Decoration", icon='PROP_ON')
            box2.prop(self, "n_beads")
            box2.prop(self, "bead_r")

    def execute(self, context: Context) -> set:
        gems = [
            o for o in context.selected_objects
            if o.get("j3d_type") == "GEM" or "gem" in o.name.lower()
        ]
        if not gems and context.active_object:
            ao = context.active_object
            if ao.get("j3d_type") not in ("CUTTER", "V_CUTTER"):
                gems = [ao]

        if not gems:
            self.report({'WARNING'}, "No gemstone selected. Select a gem first.")
            return {'CANCELLED'}

        created = []
        for gem in gems:
            dim = gem.dimensions.copy() if hasattr(gem, "dimensions") else Vector((1.0, 1.0, 0.6))
            if dim.length < 1e-4:
                dim = Vector((mm_to_bu(5.0, context),) * 2 + (mm_to_bu(3.0, context),))

            if self.style == 'WIRE':
                bm = build_wire_gallery_bmesh(
                    gem_dim_bu=dim,
                    wire_r_bu=mm_to_bu(self.wire_r, context),
                    n_rails=self.n_rails,
                    rail_spacing_bu=mm_to_bu(self.rail_spacing, context),
                    n_bridges=self.n_bridges,
                    bridge_r_bu=mm_to_bu(self.bridge_r, context),
                )
            elif self.style == 'KNIFE':
                bm = build_knife_gallery_bmesh(
                    gem_dim_bu=dim,
                    wall_bu=mm_to_bu(self.knife_wall, context),
                    height_bu=mm_to_bu(self.knife_height, context),
                    window_count=self.knife_windows,
                    window_arc_deg=self.knife_arc,
                )
            else:  # MILGRAIN
                bm = build_milgrain_gallery_bmesh(
                    gem_dim_bu=dim,
                    bead_r_bu=mm_to_bu(self.bead_r, context),
                    n_beads=self.n_beads,
                    z_offset_bu=mm_to_bu(self.milgrain_z, context),
                    wire_r_bu=mm_to_bu(self.milgrain_wire_r, context),
                )

            name = f"Gallery_{self.style}_{gem.name}"
            mesh = bpy.data.meshes.new(name + "_Mesh")
            bm.to_mesh(mesh)
            bm.free()

            obj = bpy.data.objects.new(name, mesh)
            col = gem.users_collection[0] if gem.users_collection else context.scene.collection
            col.objects.link(obj)
            obj.parent = gem
            obj.matrix_parent_inverse = Matrix.Identity(4)
            obj.location = (0.0, 0.0, 0.0)
            obj["j3d_type"] = "GALLERY"
            obj["j3d_gallery_style"] = self.style
            obj["j3d_gem_target"] = gem.name

            for poly in mesh.polygons:
                poly.use_smooth = True

            created.append(obj)

        if created:
            bpy.ops.object.select_all(action='DESELECT')
            for o in created:
                o.select_set(True)
            context.view_layer.objects.active = created[-1]

        self.report({'INFO'}, f"Gallery {self.style} generada en {len(created)} gema(s).")
        return {'FINISHED'}


classes = (J3DComm_OT_add_gallery,)


def register():
    for cls in classes:
        try:
            bpy.utils.register_class(cls)
        except Exception:
            pass


def unregister():
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except Exception:
            pass
