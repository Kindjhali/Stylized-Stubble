bl_info = {
    "name": "Stylized Hair and Stubble",
    "author": "AI Assistant",
    "version": (1, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > Stubble",
    "description": "Create stylized short hair and stubble",
    "category": "Object",
}

import bpy
from bpy.props import FloatProperty, IntProperty, BoolProperty, FloatVectorProperty, StringProperty

# Property update function to trigger live updates
def update_hair_settings(self, context):
    obj = context.active_object
    if obj and obj.type == 'MESH' and obj.particle_systems:
        # Check if we already have the hair systems
        hair_system = None
        for psys in obj.particle_systems:
            if psys.name == "StylizedHair":
                hair_system = psys
                # Update hair system
                psys.settings.count = self.hair_density
                psys.settings.hair_length = self.hair_length
                try:
                    psys.settings.radius_scale = self.hair_thickness
                except:
                    pass
                
                # Update hair color and grey percentage
                for mat in obj.material_slots:
                    if mat.material and mat.material.name.startswith("Hair_Material"):
                        update_hair_material(mat.material, self.hair_color, self.hair_grey_percentage)
                        break

def update_stubble_settings(self, context):
    obj = context.active_object
    if obj and obj.type == 'MESH' and obj.particle_systems:
        # Check if we already have the stubble system
        stubble_system = None
        for psys in obj.particle_systems:
            if psys.name == "StylizedStubble":
                stubble_system = psys
                # Update stubble system
                psys.settings.count = self.stubble_density
                psys.settings.hair_length = self.stubble_length
                try:
                    psys.settings.radius_scale = self.stubble_thickness
                except:
                    pass
                
                # Update stubble color and grey percentage
                for mat in obj.material_slots:
                    if mat.material and mat.material.name.startswith("Stubble_Material"):
                        update_stubble_material(mat.material, self.stubble_color, self.stubble_grey_percentage)
                        break

def update_transparency_settings(self, context):
    obj = context.active_object
    if obj and obj.type == 'MESH':
        # Update transparency for all relevant materials
        for mat_slot in obj.material_slots:
            if mat_slot.material and (mat_slot.material.name.startswith("Hair_Material") or 
                                      mat_slot.material.name.startswith("Stubble_Material")):
                update_material_transparency(mat_slot.material, self.transparent_scalp, self.scalp_opacity)

def update_material_transparency(material, make_transparent, opacity=0.0):
    """Update material transparency setting with custom opacity"""
    if not material or not material.use_nodes:
        return
    
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    
    # Check if we have a mix shader for transparency
    mix_node = None
    transparent_node = None
    principled_node = None
    output_node = None
    
    for node in nodes:
        if node.type == 'MIX_SHADER':
            mix_node = node
        elif node.type == 'BSDF_TRANSPARENT':
            transparent_node = node
        elif node.type == 'BSDF_PRINCIPLED':
            principled_node = node
        elif node.type == 'OUTPUT_MATERIAL':
            output_node = node
    
    # If we want any level of transparency
    if make_transparent or opacity < 1.0:
        # If we don't have the necessary nodes, create them
        if not mix_node:
            mix_node = nodes.new(type='ShaderNodeMixShader')
            mix_node.location = (280, 0)
        
        if not transparent_node:
            transparent_node = nodes.new(type='ShaderNodeBsdfTransparent')
            transparent_node.location = (100, -100)
        
        if principled_node and mix_node and transparent_node and output_node:
            # Clear existing links to output
            for link in output_node.inputs[0].links:
                links.remove(link)
            
            # Connect mix shader
            links.new(transparent_node.outputs[0], mix_node.inputs[1])
            links.new(principled_node.outputs[0], mix_node.inputs[2])
            links.new(mix_node.outputs[0], output_node.inputs[0])
            
            # Set factor - when fully transparent (opacity=0), factor should be 1
            # When fully opaque (opacity=1), factor should be 0
            if make_transparent:
                mix_node.inputs[0].default_value = 1.0
            else:
                mix_node.inputs[0].default_value = 1.0 - opacity
    else:
        # If we want scalp fully visible, connect principled directly to output
        if principled_node and output_node:
            # Clear existing links to output
            for link in output_node.inputs[0].links:
                links.remove(link)
            
            # Connect principled directly
            links.new(principled_node.outputs[0], output_node.inputs[0])

def update_hair_material(material, color, grey_percentage):
    """Update the hair material with specified color and grey percentage"""
    if not material or not material.use_nodes:
        return
    
    nodes = material.node_tree.nodes
    
    # Find color ramp for gray adjustment
    colorramp = None
    principled = None
    for node in nodes:
        if node.type == 'VALTORGB':
            colorramp = node
        elif node.type == 'BSDF_PRINCIPLED':
            principled = node
    
    # Update color
    if colorramp:
        colorramp.color_ramp.elements[0].color = color
    
    if principled:
        principled.inputs[0].default_value = color
    
    # Adjust noise scale for grey percentage
    noise_node = None
    for node in nodes:
        if node.type == 'TEX_NOISE':
            noise_node = node
            break
    
    if noise_node:
        # More grey = smaller noise scale (more variation)
        if grey_percentage > 50:
            noise_node.inputs['Scale'].default_value = 20.0 - (grey_percentage * 0.1)
        else:
            noise_node.inputs['Scale'].default_value = 12.0

def update_stubble_material(material, color, grey_percentage):
    """Update the stubble material with specified color and grey percentage"""
    update_hair_material(material, color, grey_percentage)

# Main panel in the 3D view sidebar
class HAIR_PT_Panel(bpy.types.Panel):
    bl_label = "Stylized Hair and Stubble"
    bl_idname = "HAIR_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Stubble"
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        # Target object selection
        box = layout.box()
        box.label(text="Target Object")
        box.prop(scene, "hair_target_object", text="")
        
        # Main hair settings
        box = layout.box()
        box.label(text="Hair Settings")
        box.prop(scene, "hair_density", text="Density")
        box.prop(scene, "hair_length", text="Length")
        box.prop(scene, "hair_thickness", text="Thickness")
        
        # Hair color settings
        box.prop(scene, "hair_color")
        box.prop(scene, "hair_grey_percentage", text="Grey %")
        
        # Create hair button
        row = layout.row()
        row.operator("object.create_hair", text="Create Hair").system_type = 'HAIR'
        row = layout.row()
        row.operator("object.remove_hair", text="Remove Hair").system_type = 'HAIR'
        
        layout.separator()
        
        # Stubble settings
        box = layout.box()
        box.label(text="Stubble Settings")
        box.prop(scene, "stubble_density", text="Density")
        box.prop(scene, "stubble_length", text="Length")
        box.prop(scene, "stubble_thickness", text="Thickness")
        
        # Stubble color settings
        box.prop(scene, "stubble_color")
        box.prop(scene, "stubble_grey_percentage", text="Grey %")
        
        # Create stubble button
        row = layout.row()
        row.operator("object.create_hair", text="Create Stubble").system_type = 'STUBBLE'
        row = layout.row()
        row.operator("object.remove_hair", text="Remove Stubble").system_type = 'STUBBLE'
        
        layout.separator()
        
        # Transparency settings
        box = layout.box()
        box.label(text="Transparency Settings")
        row = box.row()
        row.prop(scene, "transparent_scalp", text="Fully Transparent")
        row = box.row()
        sub = row.row()
        sub.active = not scene.transparent_scalp  # Disable opacity slider when fully transparent
        sub.prop(scene, "scalp_opacity", text="Scalp Opacity")
        
        # Apply transparency button
        row = layout.row()
        row.operator("object.update_transparency", text="Apply Transparency")
        
        # Create all systems at once
        layout.separator()
        row = layout.row()
        row.operator("object.create_hair", text="Create Both Hair & Stubble").system_type = 'BOTH'
        row = layout.row()
        row.operator("object.remove_hair", text="Remove All").system_type = 'BOTH'

# Operator to create hair/stubble
class HAIR_OT_Create(bpy.types.Operator):
    bl_idname = "object.create_hair"
    bl_label = "Create Hair/Stubble"
    bl_options = {'REGISTER', 'UNDO'}
    
    system_type: StringProperty(default='BOTH')
    
    def execute(self, context):
        scene = context.scene
        
        # Get target object
        obj = None
        if scene.hair_target_object:
            obj = scene.hair_target_object
        else:
            obj = context.active_object
        
        if obj and obj.type == 'MESH':
            if self.system_type == 'HAIR' or self.system_type == 'BOTH':
                create_hair_system_on_object(obj, context.scene)
            
            if self.system_type == 'STUBBLE' or self.system_type == 'BOTH':
                create_stubble_system_on_object(obj, context.scene)
                
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "Select or specify a mesh object first")
            return {'CANCELLED'}

# Operator to remove hair/stubble
class HAIR_OT_Remove(bpy.types.Operator):
    bl_idname = "object.remove_hair"
    bl_label = "Remove Hair/Stubble"
    bl_options = {'REGISTER', 'UNDO'}
    
    system_type: StringProperty(default='BOTH')
    
    def execute(self, context):
        scene = context.scene
        
        # Get target object
        obj = None
        if scene.hair_target_object:
            obj = scene.hair_target_object
        else:
            obj = context.active_object
        
        if obj and obj.type == 'MESH':
            # Remove particle systems based on type
            if self.system_type == 'BOTH':
                # Remove all particle systems
                while obj.particle_systems:
                    bpy.context.view_layer.objects.active = obj
                    bpy.ops.object.particle_system_remove()
            else:
                systems_to_remove = []
                for i, psys in enumerate(obj.particle_systems):
                    if (self.system_type == 'HAIR' and psys.name == "StylizedHair") or \
                       (self.system_type == 'STUBBLE' and psys.name == "StylizedStubble"):
                        systems_to_remove.append(i)
                
                # Remove in reverse order to avoid index shifting
                bpy.context.view_layer.objects.active = obj
                for i in sorted(systems_to_remove, reverse=True):
                    obj.particle_systems.active_index = i
                    bpy.ops.object.particle_system_remove()
            
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "Select or specify a mesh object first")
            return {'CANCELLED'}

# Operator to update transparency
class HAIR_OT_UpdateTransparency(bpy.types.Operator):
    bl_idname = "object.update_transparency"
    bl_label = "Update Transparency"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        scene = context.scene
        
        # Get target object
        obj = None
        if scene.hair_target_object:
            obj = scene.hair_target_object
        else:
            obj = context.active_object
        
        if obj and obj.type == 'MESH':
            # Update transparency for all materials
            for mat_slot in obj.material_slots:
                if mat_slot.material:
                    update_material_transparency(mat_slot.material, scene.transparent_scalp, scene.scalp_opacity)
            
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "Select or specify a mesh object first")
            return {'CANCELLED'}

def create_hair_material(name="Hair_Material", color=None, grey_percentage=20):
    """Create a material for stylized hair"""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    # Clear default nodes
    for node in nodes:
        nodes.remove(node)
    
    # Create basic shader
    output = nodes.new(type='ShaderNodeOutputMaterial')
    principled = nodes.new(type='ShaderNodeBsdfPrincipled')
    
    # Set up basic connections
    links.new(principled.outputs[0], output.inputs[0])
    
    # Use provided color or default
    if color is None:
        color = (0.09, 0.04, 0.02, 1.0)
    
    principled.inputs[0].default_value = color
    
    # Add color variation
    noise = nodes.new(type='ShaderNodeTexNoise')
    colorramp = nodes.new(type='ShaderNodeValToRGB')
    
    # Base color and grey variation
    colorramp.color_ramp.elements[0].color = color
    colorramp.color_ramp.elements[1].color = (0.7, 0.68, 0.66, 1.0)  # Grey/salt color
    
    # Adjust noise scale based on grey percentage
    if grey_percentage > 50:
        noise.inputs['Scale'].default_value = 20.0 - (grey_percentage * 0.1)
    else:
        noise.inputs['Scale'].default_value = 12.0
    
    noise.inputs['Detail'].default_value = 1.0
    
    # Connect nodes
    links.new(noise.outputs[0], colorramp.inputs[0])
    links.new(colorramp.outputs[0], principled.inputs[0])
    
    return mat

def create_hair_system(obj, name="StylizedHair", density=600, length=0.015, thickness=0.05, vertex_group=None, grey_group=None):
    """Create a particle system for hair/stubble that properly attaches to the mesh"""
    # Ensure active object
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    
    # Make sure we're in object mode
    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    
    # Add new particle system
    bpy.ops.object.particle_system_add()
    
    # Get the newly created particle system and rename it
    psys = obj.particle_systems[-1]
    psys.name = name
    settings = psys.settings
    settings.name = f"{name}_Settings"
    
    # Basic settings
    settings.type = 'HAIR'
    settings.render_type = 'PATH'
    settings.count = density
    settings.hair_length = length
    
    # CRITICAL - force attachment by using particle edit mode
    # This is key to fixing the attachment issue in Blender 4.x
    bpy.ops.object.mode_set(mode='PARTICLE_EDIT')
    bpy.ops.particle.select_all(action='SELECT')
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Use consistent emission settings for attachment
    # First try the legacy property name
    if hasattr(settings, 'emit_from'):
        settings.emit_from = 'FACE'
    # Then try the newer property name
    elif hasattr(settings, 'emission_source'):
        settings.emission_source = 'FACES'
    
    # Try additional attachment fixes
    try:
        # Force use of mesh geometry
        if hasattr(settings, 'use_emit_random'):
            settings.use_emit_random = False
        if hasattr(settings, 'use_modifier_stack'):
            settings.use_modifier_stack = True
        settings.distribution = 'RAND'
    except:
        pass
    
    # Try to set thickness
    try:
        settings.radius_scale = thickness
    except:
        pass
    
    # Add some randomness
    try:
        settings.length_random = 0.15
    except:
        pass
    
    # Try to set vertex group for density
    if vertex_group and vertex_group in obj.vertex_groups:
        try:
            psys.vertex_group_density = vertex_group
        except:
            pass
    
    # Try to set vertex group for grey hairs
    if grey_group and grey_group in obj.vertex_groups:
        try:
            psys.vertex_group_length = grey_group
        except:
            pass
    
    # Force update to make sure particles attach properly
    bpy.context.view_layer.update()
    
    return psys

def create_vertex_group(obj, name, verts_indices, weights=None):
    """Create or update a vertex group with given vertices"""
    # Get or create vertex group
    if name not in obj.vertex_groups:
        vgroup = obj.vertex_groups.new(name=name)
    else:
        vgroup = obj.vertex_groups[name]
    
    # Clear existing assignments
    vgroup.remove(range(len(obj.data.vertices)))
    
    # Add new vertex assignments
    if weights:
        for i, (v_idx, weight) in enumerate(zip(verts_indices, weights)):
            vgroup.add([v_idx], weight, 'REPLACE')
    else:
        vgroup.add(verts_indices, 1.0, 'REPLACE')
    
    return vgroup.name

def distribute_hair_vertices(obj, scene):
    """Determine vertices for hair and grey pattern"""
    # Get mesh dimensions
    z_coords = [v.co.z for v in obj.data.vertices]
    min_z, max_z = min(z_coords), max(z_coords)
    
    # Collect hair vertices
    hair_verts = []
    grey_hair_verts = []
    
    # Calculate which vertices to use for hair
    for i, v in enumerate(obj.data.vertices):
        # Calculate height factor (0 at bottom, 1 at top)
        if max_z > min_z:
            height = (v.co.z - min_z) / (max_z - min_z)
        else:
            height = 0.5
        
        # Hair on top half of head
        if height > 0.5:
            hair_verts.append(i)
            
            # Grey hair pattern
            grey_factor = (v.co.x * 5 + v.co.y * 7 + v.co.z * 11) % 100
            if grey_factor < scene.hair_grey_percentage:
                grey_hair_verts.append(i)
    
    # Create vertex groups
    hair_group = create_vertex_group(obj, "Hair_Vertex_Group", hair_verts)
    grey_hair_group = create_vertex_group(obj, "Grey_Hair_Group", grey_hair_verts)
    
    return hair_group, grey_hair_group

def distribute_stubble_vertices(obj, scene):
    """Determine vertices for stubble and grey pattern"""
    # Get mesh dimensions
    z_coords = [v.co.z for v in obj.data.vertices]
    y_coords = [v.co.y for v in obj.data.vertices]
    min_z, max_z = min(z_coords), max(z_coords)
    
    # Collect stubble vertices
    stubble_verts = []
    grey_stubble_verts = []
    
    # Calculate which vertices to use for stubble
    for i, v in enumerate(obj.data.vertices):
        # Calculate height factor (0 at bottom, 1 at top)
        if max_z > min_z:
            height = (v.co.z - min_z) / (max_z - min_z)
        else:
            height = 0.5
        
        # Stubble on lower face (front part of head)
        if v.co.y > 0 and 0.2 < height < 0.5:
            stubble_verts.append(i)
            
            # Grey stubble pattern (different seed than hair)
            grey_factor = (v.co.x * 7 + v.co.y * 5 + v.co.z * 13) % 100
            if grey_factor < scene.stubble_grey_percentage:
                grey_stubble_verts.append(i)
    
    # Create vertex groups
    stubble_group = create_vertex_group(obj, "Stubble_Vertex_Group", stubble_verts)
    grey_stubble_group = create_vertex_group(obj, "Grey_Stubble_Group", grey_stubble_verts)
    
    return stubble_group, grey_stubble_group

def create_hair_system_on_object(obj, scene):
    """Create just the hair system on the object"""
    # Ensure we're in object mode
    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    
    # Make sure the target object is active and selected
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    
    # Remove any existing hair system
    for i, psys in enumerate(obj.particle_systems):
        if psys.name == "StylizedHair":
            obj.particle_systems.active_index = i
            bpy.ops.object.particle_system_remove()
            break
    
    # Create material
    hair_mat = create_hair_material(
        name="Hair_Material",
        color=scene.hair_color,
        grey_percentage=scene.hair_grey_percentage
    )
    
    # Make sure we have material slots
    if len(obj.material_slots) == 0:
        bpy.ops.object.material_slot_add()
    
    # Assign material to first slot if empty
    if not obj.material_slots[0].material:
        obj.material_slots[0].material = hair_mat
    # Or add a new slot
    else:
        bpy.ops.object.material_slot_add()
        obj.material_slots[-1].material = hair_mat
    
    # Create vertex groups
    hair_group, grey_hair_group = distribute_hair_vertices(obj, scene)
    
    # Create the hair system
    hair_system = create_hair_system(
        obj,
        name="StylizedHair",
        density=scene.hair_density,
        length=scene.hair_length,
        thickness=scene.hair_thickness,
        vertex_group=hair_group,
        grey_group=grey_hair_group
    )
    
    # Apply transparency settings
    update_material_transparency(hair_mat, scene.transparent_scalp, scene.scalp_opacity)
    
    # Force update
    bpy.context.view_layer.update()
    
    return hair_system

def create_stubble_system_on_object(obj, scene):
    """Create just the stubble system on the object"""
    # Ensure we're in object mode
    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    
    # Make sure the target object is active and selected
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    
    # Remove any existing stubble system
    for i, psys in enumerate(obj.particle_systems):
        if psys.name == "StylizedStubble":
            obj.particle_systems.active_index = i
            bpy.ops.object.particle_system_remove()
            break
    
    # Create material
    stubble_mat = create_hair_material(
        name="Stubble_Material",
        color=scene.stubble_color,
        grey_percentage=scene.stubble_grey_percentage
    )
    
    # Make sure we have material slots
    if len(obj.material_slots) == 0:
        bpy.ops.object.material_slot_add()
    
    # Assign material to first slot if empty
    if not obj.material_slots[0].material:
        obj.material_slots[0].material = stubble_mat
    # Or add a new slot
    else:
        bpy.ops.object.material_slot_add()
        obj.material_slots[-1].material = stubble_mat
    
    # Create vertex groups
    stubble_group, grey_stubble_group = distribute_stubble_vertices(obj, scene)
    
    # Create the stubble system
    stubble_system = create_hair_system(
        obj,
        name="StylizedStubble",
        density=scene.stubble_density,
        length=scene.stubble_length,
        thickness=scene.stubble_thickness,
        vertex_group=stubble_group,
        grey_group=grey_stubble_group
    )
    
    # Apply transparency settings
    update_material_transparency(stubble_mat, scene.transparent_scalp, scene.scalp_opacity)
    
    # Force update
    bpy.context.view_layer.update()
    
    return stubble_system

# Register classes and properties
classes = (
    HAIR_PT_Panel,
    HAIR_OT_Create,
    HAIR_OT_Remove,
    HAIR_OT_UpdateTransparency,
)

def register():
    # Register object picker
    bpy.types.Scene.hair_target_object = bpy.props.PointerProperty(
        type=bpy.types.Object,
        name="Target",
        description="Object to add hair and stubble to"
    )
    
    # Hair properties
    bpy.types.Scene.hair_density = IntProperty(
        name="Hair Density", 
        min=100, 
        max=10000, 
        default=600,
        update=update_hair_settings
    )
    
    bpy.types.Scene.hair_length = FloatProperty(
        name="Hair Length", 
        min=0.001, 
        max=2.0, 
        default=0.015,
        update=update_hair_settings
    )
    
    bpy.types.Scene.hair_thickness = FloatProperty(
        name="Hair Thickness", 
        min=0.001, 
        max=2.0, 
        default=0.05,
        update=update_hair_settings
    )
    
    # Hair color properties
    bpy.types.Scene.hair_color = FloatVectorProperty(
        name="Hair Color",
        subtype='COLOR',
        size=4,
        min=0.0,
        max=1.0,
        default=(0.09, 0.04, 0.02, 1.0),
        update=update_hair_settings
    )
    
    bpy.types.Scene.hair_grey_percentage = IntProperty(
        name="Hair Grey %", 
        min=0, 
        max=100, 
        default=20,
        update=update_hair_settings
    )
    
    # Stubble properties with separate controls
    bpy.types.Scene.stubble_density = IntProperty(
        name="Stubble Density", 
        min=100, 
        max=10000, 
        default=800,
        update=update_stubble_settings
    )
    
    bpy.types.Scene.stubble_length = FloatProperty(
        name="Stubble Length", 
        min=0.001, 
        max=1.0, 
        default=0.004,
        update=update_stubble_settings
    )
    
    bpy.types.Scene.stubble_thickness = FloatProperty(
        name="Stubble Thickness", 
        min=0.001, 
        max=1.0, 
        default=0.04,
        update=update_stubble_settings
    )
    
    # Stubble color with separate controls
    bpy.types.Scene.stubble_color = FloatVectorProperty(
        name="Stubble Color",
        subtype='COLOR',
        size=4,
        min=0.0,
        max=1.0,
        default=(0.08, 0.03, 0.01, 1.0),  # Slightly darker than hair by default
        update=update_stubble_settings
    )
    
    bpy.types.Scene.stubble_grey_percentage = IntProperty(
        name="Stubble Grey %", 
        min=0, 
        max=100, 
        default=15,  # Less grey by default
        update=update_stubble_settings
    )
    
    # Transparency settings with separate update callback
    bpy.types.Scene.transparent_scalp = BoolProperty(
        name="Fully Transparent", 
        default=False,
        update=update_transparency_settings
    )
    
    bpy.types.Scene.scalp_opacity = FloatProperty(
        name="Scalp Opacity",
        min=0.0,
        max=1.0,
        default=1.0,
        update=update_transparency_settings
    )
    
    # Register classes
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    # Unregister classes in reverse order
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    # Delete properties
    del bpy.types.Scene.hair_target_object
    del bpy.types.Scene.hair_density
    del bpy.types.Scene.hair_length
    del bpy.types.Scene.hair_thickness
    del bpy.types.Scene.hair_color
    del bpy.types.Scene.hair_grey_percentage
    del bpy.types.Scene.stubble_density
    del bpy.types.Scene.stubble_length
    del bpy.types.Scene.stubble_thickness
    del bpy.types.Scene.stubble_color
    del bpy.types.Scene.stubble_grey_percentage
    del bpy.types.Scene.transparent_scalp
    del bpy.types.Scene.scalp_opacity

# Run register() when enabling the addon
if __name__ == "__main__":
    register()
