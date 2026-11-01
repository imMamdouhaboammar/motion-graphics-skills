# Blender MCP Command Protocol

Guidelines for scripting Blender headless and MCP sessions for motion graphics assets.

## Clay Material Assignment

To assign a universal clay preview material across all scene objects:

```python
import bpy

clay_mat = bpy.data.materials.new(name="StudioClay")
clay_mat.use_nodes = True
nodes = clay_mat.node_tree.nodes
bsdf = nodes.get("Principled BSDF")
if bsdf:
    bsdf.inputs["Base Color"].default_value = (0.7, 0.7, 0.72, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.85

for obj in bpy.context.scene.objects:
    if obj.type == "MESH":
        obj.data.materials.clear()
        obj.data.materials.append(clay_mat)
```

## Contact Shadow Catcher

Ensure floor planes declare `is_shadow_catcher = True` in Cycles render passes to output transparent background frames with intact shadows.
