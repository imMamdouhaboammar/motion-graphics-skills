---
name: blender-3d-studio
description: Bridge Claude Code with Blender via Blender MCP for physical 3D models, clay previews, and contact shadow rendering. Use when 3D in the browser looks like a toy, when real materials and shadows are required, or when building 3D mascots and physical props in Blender.
---

# Blender 3D Studio Bridge

Connects the agentic motion graphics workflow directly to Blender via MCP. This replaces lightweight browser Three.js approximations with genuine physical modeling, photorealistic ray tracing, and accurate contact shadows.

## Setup Requirements

1. Install Blender 4.2 or newer from the official blender repository.
2. Install the Blender MCP bridge:
   ```bash
   claude mcp add --scope user blender uvx blender-mcp
   ```
3. Load the companion addon script into Blender Preferences under Add-ons and enable Blender MCP.
4. Open the sidebar in Blender 3D Viewport with N, switch to the BlenderMCP tab, and click Connect.

## The Two-Stage Approval Workflow

To prevent wasted rendering time on complex 3D scenes, always follow the two-stage protocol:

### Stage 1: The Grey Clay Preview

- Model the physical asset or mascot using matte clay shaders without complex textures.
- Position a single key light and an ambient rim light.
- Render a single orthographic frame and a 3-second viewport animatic.
- Present the clay preview to the user to lock silhouette, composition, and physical proportions.

### Stage 2: Final Shading and Render

- Apply authentic PBR materials (roughness, metallic, subsurface scattering).
- Enable soft contact shadows where the model touches the floor plane.
- Execute the final render passes (beauty pass, depth pass, alpha matte pass).
- Import the rendered image sequence or ProRes video into the motion timeline.

## Scene Lighting Blueprint

| Light Source | Type | Energy | Color Temperature | Purpose |
|---|---|---|---|---|
| Key Light | Area | 150W | 5600K | Primary illumination casting soft shadow |
| Fill Light | Sun / Bounce | 40W | 4200K | Softens dark side without erasing contrast |
| Rim Light | Spot | 200W | 6500K | Separates subject silhouette from dark stage |

## Further Reading

- [references/mcp-commands.md](references/mcp-commands.md) for automated Blender Python scripts.
