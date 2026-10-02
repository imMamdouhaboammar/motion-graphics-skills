"""pfilm.py — premium 3D product-film shots in Blender, built from a JSON shot spec, rendered headless.

    blender -b --factory-startup -P pfilm.py -- --shot shots/S1.json --out renders/S1 --quality preview
    blender -b --factory-startup -P pfilm.py -- --shot shots/S1.json --out renders/S1 --quality final --stills 0.5,2.0

quality: preview (EEVEE 960x540, fast, for review) · final (EEVEE raytraced 1920x1080) · cycles (Cycles GPU/OptiX, hero shots)
--stills renders only those times (seconds) as PNGs — use it for review sheets before rendering the whole shot.
--save <file.blend> also saves the scene (to open in Blender and inspect).

Shot spec (all keys optional except duration; units are metres, the product stands at the origin):
{
  "id": "S1", "duration": 4.0, "fps": 30,
  "product": { "type": "bottle", "height": 0.22, "radius": 0.033, "liquid": 0.86, "brand": "嵐泉", "sub": "GLACIER WATER",
               "label_color": "#E9F6FA", "ink": "#0D3A47", "accent": "#5CC8E6", "cap_color": "#5CC8E6",
               "droplets": 300, "bubbles": 40, "rotate": [0, 25] },            # rotate: product spin in degrees start→end
  "set": { "floor": "gloss_black", "fog": 0.0, "backglow": "#2AA8D8", "backglow_strength": 6,
           "ground_fog": { "density": 0.08, "height": 0.08, "drift": 0.02 },           # low rolling haze at the base only
           "caustics": { "color": "#9FE8FF", "strength": 3, "scale": 6, "speed": 0.4 } },  # moving water-light lines on the backdrop
  "lights": { "preset": "hero", "tint": "#BFEFFF", "sweep": { "from": -0.35, "to": 0.35, "at": [0.3, 2.6] } },
  "camera": { "move": "dolly_in", "lens": 85, "fstop": 2.0, "target": [0, 0, 0.17],
              "from": { "dist": 0.34, "height": 0.2, "angle": -12 }, "to": { "dist": 0.22, "height": 0.18, "angle": -4 },
              "focus": "target" },
  "text": [ { "segments": [["源自 ", "#8A8A8A"], ["冰川", "#FFFFFF"]], "at": [1.2, 3.6], "y": -0.32, "size": 0.05, "reveal": "rise" } ],
  "look": { "exposure": 0.0, "contrast": "high", "vignette": 0.25 }
}
Camera moves: static · dolly_in · dolly_out · orbit · crane_up · crane_down · macro_slide · push_reveal · rack_focus.
from/to: dist (m from target, horizontal), height (m, absolute z), angle (deg around the product, 0 = front, + = right).
Everything eases in/out (Bezier keys). Text is screen-locked (parented to the camera): y = vertical position (-0.5..0.5 of frame height).
"""
import bpy, bmesh, json, math, os, sys, argparse, random
from mathutils import Vector

# Blender lays out CJK from Microsoft JhengHei (.ttc) correctly; the Noto *variable* font renders CJK as blanks.
FONT_PATHS = ["C:/Windows/Fonts/msjh.ttc", "/System/Library/Fonts/PingFang.ttc", "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"]
FONT_WEIGHTS = {"light": "C:/Windows/Fonts/msjhl.ttc", "regular": "C:/Windows/Fonts/msjh.ttc", "bold": "C:/Windows/Fonts/msjhbd.ttc"}


def hexrgb(h, a=1.0):
    h = h.lstrip("#"); c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return (*[x ** 2.2 for x in c], a)   # sRGB → linear


# ---------------------------------------------------------------- scene basics
def reset(spec):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.fps = spec.get("fps", 30)
    sc.frame_start, sc.frame_end = 1, max(2, round(spec["duration"] * sc.render.fps))
    w = bpy.data.worlds.new("World"); sc.world = w; w.use_nodes = True
    bg = w.node_tree.nodes["Background"]; bg.inputs[0].default_value = (0, 0, 0, 1); bg.inputs[1].default_value = 0
    return sc


def mat_principled(name, color="#FFFFFF", rough=0.3, metal=0.0, trans=0.0, ior=1.45, emit=None, emit_strength=0.0, alpha=1.0, coat=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = hexrgb(color)
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metal
    p.inputs["IOR"].default_value = ior
    for k in ("Transmission Weight", "Transmission"):
        if k in p.inputs: p.inputs[k].default_value = trans; break
    for k in ("Coat Weight", "Clearcoat"):
        if k in p.inputs: p.inputs[k].default_value = coat; break
    if emit:
        p.inputs["Emission Color"].default_value = hexrgb(emit); p.inputs["Emission Strength"].default_value = emit_strength
    p.inputs["Alpha"].default_value = alpha
    if trans > 0 or alpha < 1:
        try: m.surface_render_method = "BLENDED" if alpha < 1 else "DITHERED"
        except Exception: pass
        try: m.use_screen_refraction = True
        except Exception: pass
    return m


def lathe(name, prof, segs=128, uv=True, cap_top=False, cap_bottom=True):
    """Revolve a profile [(r, z), …] (bottom → top) around Z. UVs: u around, v along the profile."""
    bm = bmesh.new(); rings = []
    for (r, z) in prof:
        rings.append([bm.verts.new((r * math.cos(a), r * math.sin(a), z)) for a in (i / segs * math.tau for i in range(segs))])
    uvl = bm.loops.layers.uv.new() if uv else None
    for j in range(len(rings) - 1):
        for i in range(segs):
            f = bm.faces.new((rings[j][i], rings[j][(i + 1) % segs], rings[j + 1][(i + 1) % segs], rings[j + 1][i]))
            if uv:
                for lp, (u, v) in zip(f.loops, ((i / segs, j / (len(rings) - 1)), ((i + 1) / segs, j / (len(rings) - 1)), ((i + 1) / segs, (j + 1) / (len(rings) - 1)), (i / segs, (j + 1) / (len(rings) - 1)))):
                    lp[uvl].uv = (u, v)
    if cap_bottom and prof[0][0] > 1e-5: bm.faces.new(list(reversed(rings[0])))
    if cap_top and prof[-1][0] > 1e-5: bm.faces.new(rings[-1])
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    ob = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(ob)
    return ob



def droplet_mesh(name, items, segs=(24, 14)):
    """Many small ellipsoids as ONE mesh, built in numpy (one template sphere, transformed per droplet, one from_pydata).
    items = [(x, y, z, sx, sy, sz, rot_z), ...]. Per-droplet bmesh ops scale ~quadratically with mesh size (450 droplets at
    24x14 took ~6 min per shot); this takes well under a second."""
    import numpy as np
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=segs[0], v_segments=segs[1], radius=1)
    tv = np.array([v.co[:] for v in bm.verts], dtype=np.float32); tf = [[v.index for v in f.verts] for f in bm.faces]; bm.free()
    if not items: return None
    it = np.array(items, dtype=np.float32); n, nv = len(it), len(tv)
    c, s_ = np.cos(it[:, 6]), np.sin(it[:, 6])
    v = tv[None, :, :] * it[:, None, 3:6]                                   # scale
    x = v[..., 0] * c[:, None] - v[..., 1] * s_[:, None]; y = v[..., 0] * s_[:, None] + v[..., 1] * c[:, None]
    verts = np.stack([x + it[:, 0, None], y + it[:, 1, None], v[..., 2] + it[:, 2, None]], -1).reshape(-1, 3)
    faces = [[i + k * nv for i in f] for k in range(n) for f in tf]
    me = bpy.data.meshes.new(name); me.from_pydata(verts.tolist(), [], faces); me.update()
    for p in me.polygons: p.use_smooth = True
    ob = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(ob)
    return ob

# ---------------------------------------------------------------- product: a PET water bottle (procedural)
def bottle_profile(H, R):
    neck, shoulder = R * 0.46, H * 0.62
    p = [(R * 0.2, 0), (R * 0.82, 0.0015), (R * 0.97, 0.006), (R, 0.016)]
    for k in range(9):   # grip ribs on the lower body
        z = H * (0.1 + k * 0.045); p += [(R, z), (R * 0.965, z + H * 0.012), (R, z + H * 0.024)]
    p += [(R, shoulder)]
    for k in range(1, 13):   # shoulder curve up to the neck
        t = k / 12; p.append((neck + (R - neck) * math.cos(t * math.pi / 2) ** 1.6, shoulder + (H * 0.9 - shoulder) * t))
    p += [(neck, H * 0.93), (neck * 1.12, H * 0.935), (neck * 1.12, H * 0.945), (neck, H * 0.95), (neck, H)]
    return p


def label_texture(pr, path, w=2048, h=512):
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        return None
    img = Image.new("RGBA", (w, h), pr.get("label_color", "#E9F6FA")); d = ImageDraw.Draw(img)
    font = next((f for f in FONT_PATHS if os.path.exists(f)), None)
    F = lambda s: ImageFont.truetype(font, s) if font else ImageFont.load_default()
    ink, acc = pr.get("ink", "#0D3A47"), pr.get("accent", "#5CC8E6")
    d.rectangle([0, 0, w, 26], fill=acc); d.rectangle([0, h - 26, w, h], fill=acc)
    for cx in (w * 0.25, w * 0.75):   # brand on the front and the back of the wrap
        b = pr.get("brand", "BRAND"); fb = F(170); tw = d.textlength(b, font=fb)
        d.text((cx - tw / 2, 110), b, font=fb, fill=ink)
        s = pr.get("sub", ""); fs = F(46); tw = d.textlength(s, font=fs)
        d.text((cx - tw / 2, 330), s, font=fs, fill=ink)
        d.line([(cx - 160, 312), (cx + 160, 312)], fill=acc, width=5)
    img.save(path); return path


def build_bottle(pr, tmpdir):
    H, R = pr.get("height", 0.22), pr.get("radius", 0.033)
    prof = bottle_profile(H, R)
    shell = lathe("Bottle", prof, cap_top=False)
    sol = shell.modifiers.new("thick", "SOLIDIFY"); sol.thickness = 0.0007; sol.offset = -1
    shell.data.materials.append(mat_principled("PET", "#FFFFFF", rough=0.03, trans=1.0, ior=1.5, coat=0.3))
    objs = [shell]
    fill = pr.get("liquid", 0.86)
    if fill > 0:
        inner = [(max(0.0, r - 0.0012), z) for (r, z) in prof if z <= H * fill]
        inner.append((0.0, H * fill)) if inner[-1][0] > 0 else None
        liq = lathe("Water", [(r, z + 0.0008) for r, z in inner], cap_top=True)
        liq.data.materials.append(mat_principled("Water", "#E6F7FF", rough=0.0, trans=1.0, ior=1.333))
        objs.append(liq)
    # cap with grip ridges
    neck = R * 0.46
    cap = lathe("Cap", [(neck * 1.22, H * 0.94), (neck * 1.25, H * 0.95), (neck * 1.25, H * 1.035), (neck * 1.18, H * 1.05), (0.0, H * 1.052)], cap_top=True)
    cap.data.materials.append(mat_principled("CapPlastic", pr.get("cap_color", "#5CC8E6"), rough=0.35, coat=0.2))
    bm = bmesh.new()
    for i in range(60):
        a = i / 60 * math.tau; r = neck * 1.25
        g = bmesh.ops.create_cube(bm, size=1)["verts"]
        bmesh.ops.scale(bm, vec=(0.0012, 0.0009, H * 0.08), verts=g)
        bmesh.ops.rotate(bm, verts=g, cent=(0, 0, 0), matrix=__import__("mathutils").Matrix.Rotation(a, 3, "Z"))
        bmesh.ops.translate(bm, verts=g, vec=(r * math.cos(a), r * math.sin(a), H * 0.995))
    me = bpy.data.meshes.new("Ridges"); bm.to_mesh(me); bm.free()
    rid = bpy.data.objects.new("Ridges", me); bpy.context.collection.objects.link(rid); rid.data.materials.append(cap.data.materials[0])
    objs += [cap, rid]
    # label wrap
    if pr.get("brand"):
        z0, z1 = H * 0.22, H * 0.46
        lab = lathe("Label", [(R + 0.0004, z0), (R + 0.0004, z1)], cap_bottom=False)
        lm = mat_principled("Label", "#FFFFFF", rough=0.45)
        tex = lm.node_tree.nodes.new("ShaderNodeTexImage"); lp_ = label_texture(pr, os.path.join(tmpdir, "label.png")); tex.image = bpy.data.images.load(lp_) if lp_ else None
        lm.node_tree.links.new(tex.outputs["Color"], lm.node_tree.nodes["Principled BSDF"].inputs["Base Color"])
        lab.data.materials.append(lm); objs.append(lab)
    # condensation droplets on the glass (one merged mesh)
    n = pr.get("droplets", 0)
    if n:
        rnd = random.Random(7); items = []
        for i in range(n):
            z = rnd.uniform(0.02, H * 0.6); a = rnd.uniform(0, math.tau); s_ = rnd.uniform(0.0006, 0.0022)
            if pr.get("brand") and H * 0.22 < z < H * 0.46: continue
            rr = R + s_ * 0.2
            items.append((rr * math.cos(a), rr * math.sin(a), z, s_ * 0.55, s_, s_ * 1.25, a))
        dr = droplet_mesh("Drops", items)
        dr.data.materials.append(mat_principled("Drop", "#FFFFFF", rough=0.0, trans=1.0, ior=1.333)); objs.append(dr)
    # rising bubbles inside the water
    nb = pr.get("bubbles", 0)
    if nb and fill > 0:
        sc = bpy.context.scene; rnd = random.Random(3); bmat = mat_principled("Bubble", "#FFFFFF", rough=0.0, trans=1.0, ior=1.0)
        for i in range(nb):
            bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=12, radius=rnd.uniform(0.0006, 0.0018))
            b = bpy.context.active_object; b.data.materials.append(bmat)
            a, rr = rnd.uniform(0, math.tau), rnd.uniform(0, R * 0.8)
            x, y = rr * math.cos(a), rr * math.sin(a); z0 = rnd.uniform(0.005, H * 0.3)
            t0 = rnd.randint(sc.frame_start, sc.frame_end); dur = rnd.randint(40, 90)
            b.location = (x, y, z0); b.keyframe_insert("location", frame=t0)
            b.location = (x + rnd.uniform(-0.003, 0.003), y, min(H * fill - 0.004, z0 + H * 0.5)); b.keyframe_insert("location", frame=t0 + dur)
            for fc in b.animation_data.action.fcurves if hasattr(b.animation_data.action, "fcurves") else []:
                for k in fc.keyframe_points: k.interpolation = "LINEAR"
            objs.append(b)
    # group under one empty so the product can spin
    root = bpy.data.objects.new("Product", None); bpy.context.collection.objects.link(root)
    col = bpy.data.collections.get("ProductCol") or bpy.data.collections.new("ProductCol")
    for o in objs:
        o.parent = root
        if o.name not in col.objects: col.objects.link(o)
    root["radius"] = R
    return root, H


def build_photo_product(pr, shotdir):
    """A round product rebuilt from prep_product.py output: real silhouette -> lathe; photo projected from the front.
    Printed areas (alpha) are opaque ink/plastic, everything else is clear PET with water inside."""
    pdir = pr["photo_dir"] if os.path.isabs(pr["photo_dir"]) else os.path.join(shotdir, pr["photo_dir"])
    info = json.load(open(os.path.join(pdir, "product.json"), encoding="utf-8"))
    prof = info["profile"]; H = info["height"]; m = info["m_per_px"]
    img = bpy.data.images.load(os.path.join(pdir, info["tex"])); img.alpha_mode = "STRAIGHT"
    hpx, wpx = img.size[1], img.size[0]; bot = info["bottom_px"]; cx = info["cx_m"]
    segs = 160
    bm = bmesh.new(); rings = []
    for (r, z) in prof:
        rings.append([bm.verts.new((r * math.cos(a), r * math.sin(a), z)) for a in (i / segs * math.tau for i in range(segs))])
    uvl = bm.loops.layers.uv.new(); col = bm.loops.layers.float_color.new("front")
    for j in range(len(rings) - 1):
        for i in range(segs):
            f = bm.faces.new((rings[j][i], rings[j][(i + 1) % segs], rings[j + 1][(i + 1) % segs], rings[j + 1][i]))
            for lp in f.loops:
                x, y, z = lp.vert.co
                lp[uvl].uv = ((cx + x) / (wpx * m), 1 - (bot - z / m) / hpx)
                ny = -y / max(1e-6, math.hypot(x, y))   # 1 = facing the front (-Y)
                fr = max(0.0, min(1.0, (ny - 0.15) / 0.35))
                lp[col] = (fr, 1.0 if z > info["cap_z"] else 0.0, 0.0, 1.0)
    bm.faces.new(list(reversed(rings[0]))); bm.faces.new(rings[-1])
    me = bpy.data.meshes.new("Body"); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    body = bpy.data.objects.new("Body", me); bpy.context.collection.objects.link(body)
    sol = body.modifiers.new("thick", "SOLIDIFY"); sol.thickness = 0.0006; sol.offset = -1
    mt = bpy.data.materials.new("PrintedPET"); mt.use_nodes = True; nt = mt.node_tree; nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    glass = nt.nodes.new("ShaderNodeBsdfPrincipled"); glass.inputs["Base Color"].default_value = hexrgb(pr.get("glass_tint", "#F2FBFF"))
    glass.inputs["Roughness"].default_value = 0.02; glass.inputs["IOR"].default_value = 1.5
    glass.inputs["Transmission Weight"].default_value = 1.0
    try: glass.inputs["Coat Weight"].default_value = 0.4
    except Exception: pass
    ink = nt.nodes.new("ShaderNodeBsdfPrincipled"); ink.inputs["Roughness"].default_value = 0.5
    try: ink.inputs["Coat Weight"].default_value = 0.25
    except Exception: pass
    tex = nt.nodes.new("ShaderNodeTexImage"); tex.image = img; tex.interpolation = "Cubic"
    uvn = nt.nodes.new("ShaderNodeUVMap"); nt.links.new(uvn.outputs[0], tex.inputs[0])
    attr = nt.nodes.new("ShaderNodeAttribute"); attr.attribute_name = "front"
    sep = nt.nodes.new("ShaderNodeSeparateColor"); nt.links.new(attr.outputs["Color"], sep.inputs[0])
    mx = nt.nodes.new("ShaderNodeMath"); mx.operation = "MAXIMUM"; nt.links.new(sep.outputs[0], mx.inputs[0]); nt.links.new(sep.outputs[1], mx.inputs[1])
    mul = nt.nodes.new("ShaderNodeMath"); mul.operation = "MULTIPLY"; nt.links.new(tex.outputs["Alpha"], mul.inputs[0]); nt.links.new(mx.outputs[0], mul.inputs[1])
    nt.links.new(tex.outputs["Color"], ink.inputs["Base Color"])
    bump = nt.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = pr.get("relief", 0.0); bump.inputs["Distance"].default_value = 0.0004
    bw = nt.nodes.new("ShaderNodeRGBToBW"); nt.links.new(tex.outputs["Color"], bw.inputs[0])
    mfront = nt.nodes.new("ShaderNodeMath"); mfront.operation = "MULTIPLY"; nt.links.new(bw.outputs[0], mfront.inputs[0]); nt.links.new(sep.outputs[0], mfront.inputs[1])
    nt.links.new(mfront.outputs[0], bump.inputs["Height"]); nt.links.new(bump.outputs[0], glass.inputs["Normal"])
    mixs = nt.nodes.new("ShaderNodeMixShader"); nt.links.new(mul.outputs[0], mixs.inputs[0])
    nt.links.new(glass.outputs[0], mixs.inputs[1]); nt.links.new(ink.outputs[0], mixs.inputs[2]); nt.links.new(mixs.outputs[0], out.inputs[0])
    try:
        mt.surface_render_method = "DITHERED"; mt.use_screen_refraction = True
    except Exception: pass
    body.data.materials.append(mt)
    # the solidify inner wall must be clear PET only: printed on both walls, the label shows an offset ghost
    inner_m = mat_principled("InnerPET", pr.get("glass_tint", "#F2FBFF"), rough=0.02, trans=1.0, ior=1.5)
    body.data.materials.append(inner_m); sol.material_offset = 1; sol.material_offset_rim = 1
    objs = [body]
    # cap grip ridges: the photo only has a blurry print of them, macro shots need real geometry.
    # A ring of thin ribs just outside the cap wall, coloured like the cap (sampled from the photo's cap band).
    cap_rows = [(r, z) for (r, z) in prof if z >= info["cap_z"]]
    if cap_rows and pr.get("cap_ridges", 72):
        rc = max(r for r, _ in cap_rows); z0 = min(z for _, z in cap_rows); z1 = max(z for _, z in cap_rows)
        h = (z1 - z0) * 0.72; zc = z0 + (z1 - z0) * 0.46; n = pr.get("cap_ridges", 72)
        # average cap colour from the texture's cap band. NEVER `img.pixels[:]`: on a 4k+ label that copies tens of millions
        # of floats into a Python list and costs minutes per shot — foreach_get into numpy is ~0.1 s
        import numpy as np
        px = np.empty(wpx * hpx * 4, dtype=np.float32); img.pixels.foreach_get(px); px = px.reshape(hpx, wpx, 4)
        cy = min(hpx - 1, max(0, int((1 - (bot - zc / m) / hpx) * hpx)))
        row = px[cy, int(wpx * 0.35):int(wpx * 0.65)]; row = row[row[:, 3] > 0.5]
        capcol = list(row[:, :3].mean(0)) if len(row) else [0.2, 0.6, 0.55]
        cm = bpy.data.materials.new("CapRibs"); cm.use_nodes = True
        pb = cm.node_tree.nodes["Principled BSDF"]; pb.inputs["Base Color"].default_value = (*capcol, 1); pb.inputs["Roughness"].default_value = 0.38
        bmr = bmesh.new()
        for i in range(n):
            a = i / n * math.tau
            g = bmesh.ops.create_cube(bmr, size=1)["verts"]
            bmesh.ops.scale(bmr, vec=(rc * 0.045, rc * 0.03, h), verts=g)
            bmesh.ops.rotate(bmr, verts=g, cent=(0, 0, 0), matrix=__import__("mathutils").Matrix.Rotation(a, 3, "Z"))
            bmesh.ops.translate(bmr, verts=g, vec=((rc + rc * 0.012) * math.cos(a), (rc + rc * 0.012) * math.sin(a), zc))
        mer = bpy.data.meshes.new("CapRibs"); bmr.to_mesh(mer); bmr.free()
        rib = bpy.data.objects.new("CapRibs", mer); bpy.context.collection.objects.link(rib); rib.data.materials.append(cm)
        bev = rib.modifiers.new("bev", "BEVEL"); bev.width = rc * 0.008; bev.segments = 2
        objs.append(rib)
    fill_z = pr.get("fill_z", info["neck_z"] - 0.012)
    inner = [(max(0.0, r - 0.0011), z + 0.0008) for (r, z) in prof if z <= fill_z]
    if inner:
        inner.append((0.0, inner[-1][1]))
        liq = lathe("Water", inner, cap_top=False)
        liq.data.materials.append(mat_principled("Water", pr.get("water_tint", "#E3F6FF"), rough=0.0, trans=1.0, ior=1.333)); objs.append(liq)
    R = info["max_radius"]
    n = pr.get("droplets", 0)
    if n:
        rnd = random.Random(7); items = []
        rad_at = lambda z: next((r for (r, zz) in prof if zz >= z), R)
        for i in range(n):
            z = rnd.uniform(0.01, fill_z - 0.01); a = rnd.uniform(math.pi * 1.05, math.pi * 1.95)
            s_ = rnd.uniform(0.0005, 0.0019); rr = rad_at(z) + s_ * 0.25
            items.append((rr * math.cos(a), rr * math.sin(a), z, s_ * 0.6, s_, s_ * 1.3, a))
        dr = droplet_mesh("Drops", items)
        dr.data.materials.append(mat_principled("Drop", "#FFFFFF", rough=0.0, trans=1.0, ior=1.333)); objs.append(dr)
    nb = pr.get("bubbles", 0)
    if nb:
        sc = bpy.context.scene; rnd = random.Random(3); bmat = mat_principled("Bubble", "#FFFFFF", rough=0.0, trans=1.0, ior=1.0)
        for i in range(nb):
            bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=12, radius=rnd.uniform(0.0005, 0.0016))
            b = bpy.context.active_object; b.data.materials.append(bmat)
            a, rr = rnd.uniform(0, math.tau), rnd.uniform(0, R * 0.75)
            x, y = rr * math.cos(a), rr * math.sin(a); z0 = rnd.uniform(0.005, fill_z * 0.4)
            t0 = rnd.randint(sc.frame_start - 60, sc.frame_end); dur = rnd.randint(50, 100)
            b.location = (x, y, z0); b.keyframe_insert("location", frame=t0)
            b.location = (x + rnd.uniform(-0.002, 0.002), y, fill_z - 0.003); b.keyframe_insert("location", frame=t0 + dur)
            objs.append(b)
    root = bpy.data.objects.new("Product", None); bpy.context.collection.objects.link(root)
    col = bpy.data.collections.get("ProductCol") or bpy.data.collections.new("ProductCol")
    for o in objs:
        o.parent = root
        if o.name not in col.objects: col.objects.link(o)
    root["radius"] = R
    return root, H


# ---------------------------------------------------------------- set & lights
def area(name, loc, rot, size, energy, color="#FFFFFF", shape="RECTANGLE", size_y=None):
    L = bpy.data.lights.new(name, "AREA"); L.energy = energy; L.color = hexrgb(color)[:3]
    L.shape = shape; L.size = size
    if size_y is not None: L.size_y = size_y
    o = bpy.data.objects.new(name, L); bpy.context.collection.objects.link(o); o.location = loc; o.rotation_euler = rot
    try: o.visible_camera = False
    except Exception: pass
    return o


def look_at(o, target):
    d = Vector(target) - o.location; o.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()


def build_set(st, lt, H, sc):
    if st.get("floor", "gloss_black") != "none":
        bpy.ops.mesh.primitive_plane_add(size=20); fl = bpy.context.active_object
        fl.data.materials.append(mat_principled("Floor", "#050505", rough=st.get("floor_rough", 0.12), coat=0.6))
    if st.get("backglow"):   # studio backdrop: a dark matte sweep far behind, lit by a soft coloured spot → a natural pool of light
        bd = st.get("backdrop_dist", 0.9)
        bpy.ops.mesh.primitive_plane_add(size=1, location=(0, bd, 1.0), rotation=(math.pi / 2, 0, 0))
        b = bpy.context.active_object; b.name = "Backdrop"; b.scale = (6, 4, 1)
        b.data.materials.append(mat_principled("Backdrop", st.get("backdrop_color", "#0B0B0D"), rough=1.0))
        L = bpy.data.lights.new("BackSpot", "SPOT"); L.energy = st.get("backglow_strength", 40) * 10; L.color = hexrgb(st["backglow"])[:3]
        L.spot_size = math.radians(st.get("backglow_spread", 38)); L.spot_blend = 1.0; L.shadow_soft_size = 0.2
        o = bpy.data.objects.new("BackSpot", L); bpy.context.collection.objects.link(o)
        o.location = (0, bd - 0.9, H * st.get("backglow_height", 0.8)); look_at(o, (0, bd, H * st.get("backglow_height", 0.8)))
        try: o.visible_camera = False
        except Exception: pass
    gf = st.get("ground_fog")   # {"density": 0.08, "height": 0.08, "drift": 0.02} low rolling haze around the base only
    if gf:
        fh = gf.get("height", H * 0.35)
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0.1, fh / 2)); fb = bpy.context.active_object; fb.scale = (1.6, 1.4, fh)
        m = bpy.data.materials.new("GroundFog"); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
        out = nt.nodes.new("ShaderNodeOutputMaterial"); vol = nt.nodes.new("ShaderNodeVolumePrincipled")
        tc = nt.nodes.new("ShaderNodeTexCoord"); mp = nt.nodes.new("ShaderNodeMapping"); nz = nt.nodes.new("ShaderNodeTexNoise")
        nz.noise_dimensions = "4D"; nz.inputs["Scale"].default_value = gf.get("scale", 9.0); nz.inputs["Detail"].default_value = 4
        grad = nt.nodes.new("ShaderNodeSeparateXYZ"); fall = nt.nodes.new("ShaderNodeMapRange")   # denser at the floor, fading up
        fall.inputs["From Min"].default_value = 0.0; fall.inputs["From Max"].default_value = fh; fall.inputs["To Min"].default_value = 1.0; fall.inputs["To Max"].default_value = 0.0
        mul = nt.nodes.new("ShaderNodeMath"); mul.operation = "MULTIPLY"; mul2 = nt.nodes.new("ShaderNodeMath"); mul2.operation = "MULTIPLY"
        mul2.inputs[1].default_value = gf.get("density", 0.3) * 10
        nt.links.new(tc.outputs["Object"], mp.inputs[0]); nt.links.new(mp.outputs[0], nz.inputs["Vector"])
        tcw = nt.nodes.new("ShaderNodeTexCoord"); nt.links.new(tcw.outputs["Generated"], grad.inputs[0])
        sepw = nt.nodes.new("ShaderNodeNewGeometry"); sp = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(sepw.outputs["Position"], sp.inputs[0])
        nt.links.new(sp.outputs["Z"], fall.inputs["Value"])
        nt.links.new(nz.outputs["Fac"], mul.inputs[0]); nt.links.new(fall.outputs["Result"], mul.inputs[1]); nt.links.new(mul.outputs[0], mul2.inputs[0])
        nt.links.new(mul2.outputs[0], vol.inputs["Density"]); vol.inputs["Color"].default_value = hexrgb(gf.get("color", "#DDE6EE"))
        nt.links.new(vol.outputs[0], out.inputs["Volume"])
        fps_ = sc.render.fps   # drift: the noise evolves over time (W) and slides sideways
        nz.inputs["W"].default_value = 0.0; nz.inputs["W"].keyframe_insert("default_value", frame=1)
        nz.inputs["W"].default_value = sc.frame_end / fps_ * gf.get("evolve", 0.25); nz.inputs["W"].keyframe_insert("default_value", frame=sc.frame_end)
        mp.inputs["Location"].default_value = (0, 0, 0); mp.inputs["Location"].keyframe_insert("default_value", frame=1)
        mp.inputs["Location"].default_value = (gf.get("drift", 0.02) * sc.frame_end / fps_ * 10, 0, 0); mp.inputs["Location"].keyframe_insert("default_value", frame=sc.frame_end)
        fb.data.materials.append(m)
        try: fb.visible_shadow = False
        except Exception: pass
    ca = st.get("caustics")   # {"color": "#9FE8FF", "strength": 3, "scale": 6, "speed": 0.4} moving water-light lines on the backdrop
    if ca and bpy.data.objects.get("Backdrop") is None:
        bd = st.get("backdrop_dist", 0.9)
        bpy.ops.mesh.primitive_plane_add(size=1, location=(0, bd, 1.0), rotation=(math.pi / 2, 0, 0)); b = bpy.context.active_object; b.name = "Backdrop"; b.scale = (6, 4, 1)
        b.data.materials.append(mat_principled("BackdropBase", st.get("backdrop_color", "#0B0B0D"), rough=1.0))
    if ca:
        b = bpy.data.objects.get("Backdrop")
        m = bpy.data.materials.new("Caustics"); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
        out = nt.nodes.new("ShaderNodeOutputMaterial"); em = nt.nodes.new("ShaderNodeEmission"); base = nt.nodes.new("ShaderNodeBsdfPrincipled")
        base.inputs["Base Color"].default_value = hexrgb(st.get("backdrop_color", "#0B0B0D")); base.inputs["Roughness"].default_value = 1.0
        tc = nt.nodes.new("ShaderNodeTexCoord"); vr = nt.nodes.new("ShaderNodeTexVoronoi"); vr.voronoi_dimensions = "4D"; vr.feature = "DISTANCE_TO_EDGE"
        vr.inputs["Scale"].default_value = ca.get("scale", 6.0) * 8   # the backdrop is 6 m wide: ~50 cells across reads as water light
        # warp at the cell frequency so every cell edge bends (caustic lines are curved, never polygon edges)
        warp = nt.nodes.new("ShaderNodeTexNoise"); warp.inputs["Scale"].default_value = ca.get("scale", 6.0) * 7; warp.inputs["Detail"].default_value = 3
        mixv = nt.nodes.new("ShaderNodeVectorMath"); mixv.operation = "ADD"
        sc_ = nt.nodes.new("ShaderNodeVectorMath"); sc_.operation = "SCALE"; sc_.inputs["Scale"].default_value = 0.9 / (ca.get("scale", 6.0) * 8)
        nt.links.new(tc.outputs["Object"], warp.inputs["Vector"]); nt.links.new(warp.outputs["Color"], sc_.inputs[0])
        nt.links.new(tc.outputs["Object"], mixv.inputs[0]); nt.links.new(sc_.outputs[0], mixv.inputs[1]); nt.links.new(mixv.outputs[0], vr.inputs["Vector"])
        ramp = nt.nodes.new("ShaderNodeValToRGB"); cr = ramp.color_ramp
        cr.interpolation = "EASE"; cr.elements[0].position = 0.0; cr.elements[0].color = (1, 1, 1, 1)
        cr.elements[1].position = ca.get("line", 0.022); cr.elements[1].color = (0, 0, 0, 1)
        nt.links.new(vr.outputs["Distance"], ramp.inputs[0])
        tint = nt.nodes.new("ShaderNodeMixRGB"); tint.blend_type = "MULTIPLY"; tint.inputs[0].default_value = 1.0; tint.inputs[2].default_value = hexrgb(ca.get("color", "#9FE8FF"))
        nt.links.new(ramp.outputs[0], tint.inputs[1]); nt.links.new(tint.outputs[0], em.inputs["Color"]); em.inputs["Strength"].default_value = ca.get("strength", 0.35)
        add = nt.nodes.new("ShaderNodeAddShader"); nt.links.new(base.outputs[0], add.inputs[0]); nt.links.new(em.outputs[0], add.inputs[1]); nt.links.new(add.outputs[0], out.inputs[0])
        fps_ = sc.render.fps
        vr.inputs["W"].default_value = 0.0; vr.inputs["W"].keyframe_insert("default_value", frame=1)
        vr.inputs["W"].default_value = sc.frame_end / fps_ * ca.get("speed", 0.4); vr.inputs["W"].keyframe_insert("default_value", frame=sc.frame_end)
        b.data.materials.clear(); b.data.materials.append(m)
    if st.get("fog"):
        sc.world.node_tree.nodes["Background"].inputs[1].default_value = 0
        vol = sc.world.node_tree.nodes.new("ShaderNodeVolumeScatter"); vol.inputs["Density"].default_value = st["fog"]
        sc.world.node_tree.links.new(vol.outputs[0], sc.world.node_tree.nodes["World Output"].inputs["Volume"])
    tint = lt.get("tint", "#FFFFFF"); pre = lt.get("preset", "hero")
    before = set(o for o in bpy.data.objects if o.name != "BackSpot")
    # rim strips: two tall thin softboxes behind-left / behind-right → bright edges on glass, dark body
    # close-ups: a tall rim strip mirrored along the whole silhouette reads as a white cut-out outline; use a short,
    # weak strip at the framed region only, so the edge gets a broken highlight, not a continuous stroke
    cu = lt.get("closeup"); rz = lt.get("closeup_z", H * 0.55)
    # (a smaller strip is *brighter* per area, and grazing reflections show radiance, so close-ups turn the rims off by
    # default — the sweep, top and key still model the edges; set lights.closeup_rim to force a little back)
    # close-ups get a wide, dim softbox instead: ~20x lower radiance → a soft gradient along the edge that still shapes the glass
    # The edge line's WIDTH is the strip's angular width; its brightness is the strip's radiance (energy / area). In close-ups
    # the same 3 cm strip draws a thick cut-out stroke, so: a much thinner strip (4 mm) at the same radiance → a fine line.
    base_e, base_w, base_h = lt.get("rim", 45), 0.03, H * 1.6
    if cu:
        w_, h_ = 0.004, H * 0.5
        rim_e = lt.get("closeup_rim", base_e * (w_ * h_) / (base_w * base_h))
    else:
        w_, h_, rim_e = base_w, base_h, base_e
    for s in (-1, 1):
        if rim_e <= 0: break
        o = area(f"Rim{s}", (s * 0.28, 0.32, rz if cu else H * 0.55), (0, 0, 0), w_, rim_e, tint, "RECTANGLE", h_)
        look_at(o, (0, 0, rz if cu else H * 0.55))
    if pre in ("hero", "three_point"):
        k = area("Key", (-0.35, -0.3, H * 1.6), (0, 0, 0), 0.35, lt.get("key", 5), "#FFFFFF"); look_at(k, (0, 0, H * 0.5))
    if pre in ("hero", "top_soft"):
        t = area("Top", (0, 0, H * 2.4), (0, 0, 0), 0.3, lt.get("top", 4), tint); look_at(t, (0, 0, 0))
    sw = lt.get("sweep")
    if sw:   # a thin strip light travelling across the front: the highlight sweeps over the product
        o = area("Sweep", (sw.get("from", -0.35), -0.3, H * 0.6), (0, 0, 0), 0.02, lt.get("sweep_energy", 8), tint, "RECTANGLE", H * 1.8)
        look_at(o, (0, 0, H * 0.6)); f0, f1 = [max(1, round(t * sc.render.fps)) for t in sw.get("at", [0, 2])]
        o.keyframe_insert("location", frame=f0); o.location.x = sw.get("to", 0.35); o.keyframe_insert("location", frame=f1)
    rv = lt.get("reveal")   # [t0, t1] seconds: all lights fade up from 0 (a reveal from darkness)
    if rv:
        f0, f1 = [max(1, round(t * sc.render.fps) + 1) for t in rv]
        for o in set(bpy.data.objects) - before:
            if o.type == "LIGHT":
                e = o.data.energy; o.data.energy = 0.0; o.data.keyframe_insert("energy", frame=f0)
                o.data.energy = e; o.data.keyframe_insert("energy", frame=f1)
    prod = bpy.data.collections.get("ProductCol")
    if prod:
        for o in set(bpy.data.objects) - before:
            if o.type == "LIGHT" and o.name != "BackSpot":
                try: o.light_linking.receiver_collection = prod
                except Exception: pass


# ---------------------------------------------------------------- camera
SENSOR_H = 36 * 9 / 16   # 16:9 frame on a 36 mm wide sensor


def resolve(p, H, lens, R=0.033):
    """A camera key may give "fill" (fraction of frame height the subject spans) and "region" [z0, z1] (which part of
    the product is the subject; default the whole product) instead of a raw dist. Returns (key with dist, subject centre z)."""
    q = dict(p)
    z0, z1 = q.get("region", [0, H])
    if "fill" in q:
        visible = (z1 - z0) / max(0.05, q["fill"]); q["dist"] = visible * lens / SENSOR_H + R
    q.setdefault("height", (z0 + z1) / 2)
    return q, (z0 + z1) / 2


def cam_pos(target, p):
    a = math.radians(p.get("angle", 0)); d = p.get("dist", 0.4)
    return Vector((target[0] + d * math.sin(a), target[1] - d * math.cos(a), p.get("height", target[2])))


def build_camera(cs, sc, H, product):
    cd = bpy.data.cameras.new("Cam"); cam = bpy.data.objects.new("Cam", cd); bpy.context.collection.objects.link(cam); sc.camera = cam
    cd.lens = cs.get("lens", 85); cd.sensor_width = 36; cd.clip_start = 0.005
    lens = cs.get("lens", 85); R = cs.get("_radius", 0.033)
    A0, zc0 = resolve(cs.get("from", {"fill": 0.8}), H, lens, R)
    B0, zc1 = resolve(cs.get("to", cs.get("from", {"fill": 0.8})), H, lens, R)
    tgt = cs.get("target", [0, 0, zc0])
    if "target" not in cs and "target_to" not in cs and abs(zc1 - zc0) > 1e-4: cs["target_to"] = [0, 0, zc1]
    k = cs.get("speed_scale", 1.0)   # shrink the move toward its start (match a slower reference shot without re-planning)
    if k != 1.0:
        for f in ("dist", "height", "angle"):
            if f in A0 and f in B0: B0[f] = A0[f] + (B0[f] - A0[f]) * k
        if "target_to" in cs: cs["target_to"] = [t0 + (t1 - t0) * k for t0, t1 in zip(tgt, cs["target_to"])]
    cs["from"], cs["to"] = A0, B0
    aim = bpy.data.objects.new("Aim", None); bpy.context.collection.objects.link(aim); aim.location = tgt
    tr = cam.constraints.new("TRACK_TO"); tr.target = aim; tr.track_axis = "TRACK_NEGATIVE_Z"; tr.up_axis = "UP_Y"
    mv = cs.get("move", "dolly_in"); fps = sc.render.fps; f1 = sc.frame_end
    A = cs.get("from", {"dist": 0.4, "height": tgt[2], "angle": 0}); Bp = cs.get("to", A)
    defaults = {
        "static": (A, A), "dolly_in": (A, Bp), "dolly_out": (A, Bp), "crane_up": (A, Bp), "crane_down": (A, Bp),
        "orbit": (A, Bp), "macro_slide": (A, Bp), "push_reveal": (A, Bp), "rack_focus": (A, A),
    }
    p0, p1 = defaults.get(mv, (A, Bp))
    cam.location = cam_pos(tgt, p0); cam.keyframe_insert("location", frame=1)
    if mv == "orbit":   # true arc: key every few frames so the path curves around the product
        n = max(2, f1 // 6)
        for i in range(n + 1):
            t = i / n; e = t * t * (3 - 2 * t)
            p = {k: p0.get(k, 0) + (p1.get(k, 0) - p0.get(k, 0)) * e for k in ("dist", "height", "angle")}
            cam.location = cam_pos(tgt, p); cam.keyframe_insert("location", frame=1 + round(t * (f1 - 1)))
    else:
        cam.location = cam_pos(tgt, p1); cam.keyframe_insert("location", frame=f1)
    if "target_to" in cs:   # the aim point can travel too (macro slides along the surface)
        aim.keyframe_insert("location", frame=1); aim.location = cs["target_to"]; aim.keyframe_insert("location", frame=f1)
    if cs.get("lens_to"):
        cd.keyframe_insert("lens", frame=1); cd.lens = cs["lens_to"]; cd.keyframe_insert("lens", frame=f1)
    # depth of field
    if cs.get("fstop") or cs.get("dof_depth") or cs.get("dof", "medium") != "off":
        cd.dof.use_dof = True
        # depth of field ≈ 2·N·c·s² / f²  →  N = depth·f² / (2·c·s²); c = 0.03 mm circle of confusion
        s_ = max(0.05, min(A0.get("dist", 0.4), B0.get("dist", 0.4)))
        depth = cs.get("dof_depth") or {"shallow": R * 0.8, "medium": R * 2.0, "deep": R * 5.0}.get(cs.get("dof", "medium"), R * 2.0)
        auto = depth * (lens / 1000) ** 2 / (2 * 0.00003 * s_ ** 2)
        cd.dof.aperture_fstop = cs.get("fstop") or max(1.8, min(22.0, auto))
        if mv == "rack_focus" and "focus_from" in cs:
            cd.dof.focus_distance = cs["focus_from"]; cd.keyframe_insert("dof.focus_distance", frame=1)
            cd.dof.focus_distance = cs["focus_to"]; cd.keyframe_insert("dof.focus_distance", frame=f1)
        else:
            # focus on the surface facing the camera: an empty R in front of the aim point, riding with it
            fo = bpy.data.objects.new("Focus", None); bpy.context.collection.objects.link(fo); fo.parent = aim
            ang = math.radians(cs["from"].get("angle", 0)); fo.location = (R * math.sin(ang), -R * math.cos(ang), 0)
            cd.dof.focus_object = fo if cs.get("focus", "front") == "front" else aim
    # product spin
    rot = cs.get("_spin")
    return cam


def spin_product(root, deg, sc):
    if not deg: return
    root.rotation_euler.z = math.radians(deg[0]); root.keyframe_insert("rotation_euler", frame=1)
    root.rotation_euler.z = math.radians(deg[1]); root.keyframe_insert("rotation_euler", frame=sc.frame_end)


# ---------------------------------------------------------------- screen-locked typography
def build_text(items, cam, sc):
    font = next((f for f in FONT_PATHS if os.path.exists(f)), None)
    fonts = {}
    def font_for(wt):
        path = FONT_WEIGHTS.get(wt or "regular")
        path = path if path and os.path.exists(path) else font
        if path and path not in fonts: fonts[path] = bpy.data.fonts.load(path)
        return fonts.get(path)
    fps = sc.render.fps; cd = cam.data; D = 0.5   # text plane at 0.5 m in front of the lens
    frame_h = D * cd.sensor_width / cd.lens * 9 / 16   # visible height at distance D (16:9, sensor fit horizontal)
    for n, it in enumerate(items):
        segs = it.get("segments") or [[it.get("content", ""), it.get("color", "#FFFFFF")]]
        size = it.get("size", 0.045) * frame_h / 0.72; y = it.get("y", -0.3) * frame_h   # size = glyph height as a fraction of frame height
        parts = []
        for k, (txt, col) in enumerate(segs):
            cu = bpy.data.curves.new(f"T{n}_{k}", "FONT"); cu.body = txt; cu.size = size; cu.align_y = "CENTER"
            f_ = font_for(it.get("weight"))
            if f_: cu.font = f_
            if it.get("weight_offset"): cu.offset = it["weight_offset"] * size
            o = bpy.data.objects.new(f"T{n}_{k}", cu); bpy.context.collection.objects.link(o)
            m = mat_principled(f"TM{n}_{k}", "#000000", rough=1, emit=col, emit_strength=it.get("glow", 1.2), alpha=1.0)
            try: m.surface_render_method = "BLENDED"
            except Exception: pass
            o.data.materials.append(m); parts.append((o, m))
        bpy.context.view_layer.update()
        widths = [o.dimensions.x for o, _ in parts]; gap = size * 0.12; total = sum(widths) + gap * (len(parts) - 1)
        x = -total / 2
        t_in, t_out = it.get("at", [0, sc.frame_end / fps])
        for (o, m), w in zip(parts, widths):
            o.parent = cam; o.location = (x, y, -D); x += w + gap
            p = m.node_tree.nodes["Principled BSDF"]; a = p.inputs["Alpha"]
            fi, fo = max(1, round(t_in * fps)), round(t_out * fps)
            stag = parts.index((o, m)) * it.get("stagger", 0.12) * fps
            a.default_value = 0; a.keyframe_insert("default_value", frame=fi + stag)
            a.default_value = 1; a.keyframe_insert("default_value", frame=fi + stag + round(0.45 * fps))
            if fo < sc.frame_end:
                a.keyframe_insert("default_value", frame=fo - round(0.35 * fps)); a.default_value = 0; a.keyframe_insert("default_value", frame=fo)
            if it.get("reveal", "rise") == "rise":
                o.location.y = y - size * 0.35; o.keyframe_insert("location", frame=fi + stag)
                o.location.y = y; o.keyframe_insert("location", frame=fi + stag + round(0.6 * fps))


# ---------------------------------------------------------------- render settings
def configure(sc, quality, look):
    r = sc.render
    if quality in ("cycles", "final", "preview"):
        r.engine = "CYCLES"
        prefs = bpy.context.preferences.addons["cycles"].preferences
        for t in ("OPTIX", "CUDA"):
            try:
                prefs.compute_device_type = t; prefs.get_devices()
                for d in prefs.devices: d.use = d.type == t
                sc.cycles.device = "GPU"; break
            except Exception: continue
        sc.cycles.samples = {"preview": 48, "final": 192, "cycles": 384}[quality]; sc.cycles.use_denoising = True
        try: sc.cycles.denoiser = "OPTIX"
        except Exception: pass
        sc.cycles.transmission_bounces = 16; sc.cycles.max_bounces = 20; sc.cycles.caustics_refractive = True
        sc.cycles.use_adaptive_sampling = True
        r.resolution_x, r.resolution_y = (960, 540) if quality == "preview" else (1920, 1080)
    else:
        r.engine = "BLENDER_EEVEE"; e = sc.eevee
        for k, v in (("use_raytracing", True), ("use_shadows", True), ("use_gtao", True)):
            try: setattr(e, k, v)
            except Exception: pass
        try: e.taa_render_samples = 16 if quality == "preview" else 96
        except Exception: pass
        try: e.ray_tracing_options.resolution_scale = "2" if quality == "preview" else "1"
        except Exception: pass
        r.resolution_x, r.resolution_y = (960, 540) if quality == "preview" else (1920, 1080)
    vs = sc.view_settings
    try: vs.view_transform = "AgX"
    except Exception: pass
    for lk in ("AgX - " + {"high": "Medium High Contrast", "punchy": "Punchy", "normal": "Base Contrast"}.get(look.get("contrast", "high"), "Medium High Contrast"), "Medium High Contrast", "None"):
        try: vs.look = lk; break
        except Exception: continue
    vs.exposure = look.get("exposure", 0.0)
    r.image_settings.file_format = "PNG"; r.use_motion_blur = look.get("motion_blur", True)
    try: r.use_persistent_data = True
    except Exception: pass
    # compositor: a soft vignette + subtle glare so highlights bloom like a lens
    try:
        sc.use_nodes = True; nt = sc.node_tree; nt.nodes.clear()
        rl = nt.nodes.new("CompositorNodeRLayers"); comp = nt.nodes.new("CompositorNodeComposite")
        gl = nt.nodes.new("CompositorNodeGlare"); gl.glare_type = "FOG_GLOW"
        try: gl.quality = "HIGH"; gl.threshold = 0.9; gl.mix = -0.7
        except Exception: pass
        nt.links.new(rl.outputs["Image"], gl.inputs[0]); nt.links.new(gl.outputs[0], comp.inputs[0])
    except Exception:
        pass


# ---------------------------------------------------------------- main
def measure(sc, cam, root, H, info_tex=None):
    """Per shot, sampled at 5 moments: how much of the frame the product covers (height and area of its projected
    bounding box), whether it is cut by the frame, and — for photo products — texture pixels per screen pixel on the
    framed part (< 0.8 means the photo is too small for this close-up: it will look soft)."""
    from bpy_extras.object_utils import world_to_camera_view
    objs = [o for o in bpy.data.collections["ProductCol"].objects if o.type == "MESH"] if bpy.data.collections.get("ProductCol") else []
    out = []
    for k in range(5):
        f = round(sc.frame_start + (sc.frame_end - sc.frame_start) * k / 4); sc.frame_set(f)
        xs, ys = [], []
        for o in objs:
            for c in o.bound_box:
                v = world_to_camera_view(sc, cam, o.matrix_world @ Vector(c))
                if v.z > 0: xs.append(v.x); ys.append(v.y)
        if not xs: continue
        x0, x1, y0, y1 = max(0, min(xs)), min(1, max(xs)), max(0, min(ys)), min(1, max(ys))
        cut = min(xs) < -0.02 or max(xs) > 1.02 or min(ys) < -0.02 or max(ys) > 1.02
        rec = {"t": round((f - 1) / sc.render.fps, 2), "fill_h": round(y1 - y0, 3), "fill_area": round((x1 - x0) * (y1 - y0), 3),
               "center": [round((x0 + x1) / 2, 3), round((y0 + y1) / 2, 3)], "cropped_by_frame": cut}
        if info_tex:   # texture density at the frame centre: metres per screen pixel vs metres per texture pixel
            d = (cam.matrix_world.translation - bpy.data.objects["Aim"].matrix_world.translation).length
            m_per_screen_px = 2 * d * math.tan(cam.data.angle / 2) / sc.render.resolution_x
            rec["texel_ratio"] = round(m_per_screen_px / info_tex, 2)   # < 1: fewer texture pixels than screen pixels
        out.append(rec)
    return out


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser(); ap.add_argument("--shot", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--quality", default="preview", choices=["preview", "final", "cycles", "eevee"]); ap.add_argument("--stills")
    ap.add_argument("--frames"); ap.add_argument("--save")
    a = ap.parse_args(argv)
    spec = json.load(open(a.shot, encoding="utf-8")); os.makedirs(a.out, exist_ok=True)
    sc = reset(spec)
    pr = spec.get("product", {"type": "bottle"})
    root, H = build_photo_product(pr, os.path.dirname(os.path.abspath(a.shot))) if pr.get("type") == "photo" else build_bottle(pr, a.out)
    spin_product(root, pr.get("rotate"), sc)
    lt_ = dict(spec.get("lights", {})); cam_ = spec.get("camera", {})
    reg = (cam_.get("from") or {}).get("region")
    if "closeup" not in lt_ and reg and (reg[1] - reg[0]) < H * 0.35: lt_["closeup"] = True
    if lt_.get("closeup") and reg: lt_.setdefault("closeup_z", (reg[0] + reg[1]) / 2)
    build_set(spec.get("set", {}), lt_, H, sc)
    cs = spec.get("camera", {}); cs["_radius"] = root.get("radius", cs.get("_radius", 0.033))
    cam = build_camera(cs, sc, H, root)
    if spec.get("text") and spec.get("text_mode") == "3d": build_text(spec["text"], cam, sc)   # titles normally go on in finish.py (2D, crisp)
    configure(sc, a.quality, spec.get("look", {}))
    tex_m = None
    if pr.get("type") == "photo":
        pdir = pr["photo_dir"] if os.path.isabs(pr["photo_dir"]) else os.path.join(os.path.dirname(os.path.abspath(a.shot)), pr["photo_dir"])
        tex_m = json.load(open(os.path.join(pdir, "product.json"), encoding="utf-8"))["m_per_px"]
    m = measure(sc, cam, root, H, tex_m)
    warn = []
    if m:
        mh = max(r["fill_h"] for r in m); ma = max(r["fill_area"] for r in m)
        if mh < 0.6 and not spec.get("allow_small"): warn.append(f"product small: max height fill {mh:.2f} (< 0.6)")
        if ma < 0.18 and not spec.get("allow_small"): warn.append(f"product covers only {ma:.0%} of the frame (< 18%): a tall thin product "
                                                               f"needs a tighter crop, a lower/closer angle, or a title filling the empty side")
        tr = [r["texel_ratio"] for r in m if "texel_ratio" in r]
        if tr and min(tr) < 0.8: warn.append(f"texture too soft for this close-up: {min(tr):.2f} texture px per screen px (< 0.8)")
    json.dump({"id": spec.get("id"), "samples": m, "warnings": warn}, open(os.path.join(a.out, "meta.json"), "w"), indent=1)
    for w_ in warn: print("PFILM_WARN", spec.get("id"), w_)
    sc.frame_set(1)
    if a.save: bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(a.save))
    if a.stills:
        for t in [float(x) for x in a.stills.split(",")]:
            f = min(sc.frame_end, max(1, round(t * sc.render.fps) + 1)); sc.frame_set(f)
            sc.render.filepath = os.path.join(os.path.abspath(a.out), f"still_{t:05.2f}.png"); bpy.ops.render.render(write_still=True)
    else:
        if a.frames:
            f0, f1 = [int(x) for x in a.frames.split(":")]; sc.frame_start, sc.frame_end = f0, f1
        sc.render.filepath = os.path.join(os.path.abspath(a.out), "f")
        bpy.ops.render.render(animation=True)
    print("PFILM_DONE", a.out)


main()
