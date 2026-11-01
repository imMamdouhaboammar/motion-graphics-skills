# Blender 3D Scene Standards

Rules applied when building or rendering 3D scenes via Blender MCP.

1. **Two-Stage Verification**: Always present a matte grey clay preview to the user before committing to full Cycles rendering passes.
2. **Floor Contact Shadows**: When placing physical props or mascots on a ground plane, configure the floor material as an active shadow catcher (`is_shadow_catcher = True`) so contact shadows render cleanly over transparent or composite backgrounds.
3. **Three-Point Lighting**: Every primary 3D subject must receive a designated key light (area light, 150W), a subtle fill light (bounce, 40W), and a distinct rim light (spot, 200W) to separate silhouettes from dark stages.
4. **Physical Texture**: Avoid perfectly flat or plasticky surfaces. Apply subtle surface roughness, micro-scratches, or bevelled edges to maintain photorealistic weight.
