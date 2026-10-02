# vector_rig — 不拼接的 2D 向量角色

**所有 2D 向量風格（hyperframes 等 HTML/SVG 引擎）的角色一律用這套做。** 不准用「頭一張圖＋身體一張圖＋長方形手臂」拼角色。

## 為什麼
拼出來的角色會：手浮空、手臂硬黏在身體邊、沒脖子、每鏡比例不同、關節處兩層描邊。
這套的做法是：
- **骨架**：脖子、肩、肘、腕、髖、膝是真的關節；手臂與腿是沿骨架長出的漸細膠囊，手與鞋固定在末端 → 永遠接著。
- **一條外輪廓**：每個深度層（後側肢體／身體＋頭／前側肢體）只填色不描邊，再由 SVG 濾鏡沿整層剪影描**一次**邊
  → 重疊處自然融成一體、沒有接縫；前手臂疊在身體上仍有正確的遮擋線。線寬跟著角色縮放（特寫線條會變粗）。
- **同一份角色定義**：每一鏡只給姿勢參數，造型、比例、配色永遠一致。

## 用法（HyperFrames / 任何 HTML）
```html
<script src="assets/rig.js"></script>
<svg id="stage" width="1920" height="1080" viewBox="0 0 1920 1080"></svg>
<script>
  const hero = VRig.make(document.getElementById('stage'), VRig.presets.chestnut({ scale: 1.2, shirt: '#E9B43A' }));
  const st = { arm: 20 };
  const draw = () => hero.pose({ x: 960, y: 900, expr: 'happy', armR: [st.arm, -25], handR: 'wave' });
  const tl = gsap.timeline({ paused: true, onUpdate: draw });   // HyperFrames seeks the timeline; onUpdate redraws
  tl.to(st, { arm: 150, duration: 0.4, ease: 'back.out(1.6)' }, 0.1);
  draw(); window.__timelines['main'] = tl;
</script>
```
每一格都由 `pose()` 從參數重畫（純函式），所以隨意跳格渲染結果都一樣。

## pose 參數
| 參數 | 說明 |
|---|---|
| `x, y` | 兩腳之間的地面點（畫面座標） |
| `scale` | 大小（中景 ≈ 1，特寫 2–3） |
| `facing` | 1 朝右、-1 朝左 |
| `turn` | 0 正面 … 0.8 接近 3/4 側（**目前 3/4 側身較弱，主要用 0–0.4**） |
| `lean`, `squash` | 身體傾斜（度）、壓扁拉長（-0.1…0.1） |
| `head`, `headY` | 頭部傾斜（度）、上下擺動 |
| `armL/armR: [肩, 肘]` | 角度（度）；0 = 自然下垂，90 = 平舉向外，150–170 = 高舉；肘角負值往上彎 |
| `legL/legR: [髖, 膝]` | 正值 = 張開；跑步用前後相反的值 |
| `handL/handR` | `fist`、`open`、`wave`、`point` |
| `expr` | `neutral happy grin smug shock scream cry sad angry deadpan love evil`，或自訂物件 `{eyes, mouth, brows, blush, tears, sweat}` |
| `blush`, `sweat` | 0–1 疊加 |
| `prop` | `{ hand: 'R', draw(g, hand, s) }` 在手的座標系畫手上的東西（手機、杯子…），會跟著手動 |

常用姿勢：揮手 `armR:[150,-25], handR:'wave'` · 驚嚇雙手舉高 `armL/armR:[160,-15], handL/R:'open', expr:'scream'` ·
指向 `armR:[90,0], handR:'point'` · 拿手機看 `armR:[20,-110], prop: phone` · 雙手叉腰 `armL/armR:[35,-120]`

## 做新角色
`VRig.presets` 裡是造型範本（`chestnut` 栗子鍋蓋頭＋連帽 T、`sprout` 平頭＋小芽＋眼鏡）。新角色用
`VRig.make(svg, { ...VRig.DEFAULT, hair: (r, cy, turn) => '<svg path>', hairColor, skin, shirt, pants, shoe, headR, torsoH, … })`，
髮型寫成頭部座標（中心 0,cy、半徑 r）的一條 path。比例參數：`headR torsoH shoulderW hipW legLen armLen armR legR handR neckLen`。
全部都是原創造型；使用者提供自家角色設計圖時，照著設計圖把髮型、配色、比例填進去。

## 驗證
`_smoke/rig/`（設定圖、特寫、與舊拼接版的比較）與 `_smoke/rigHF/`（HyperFrames 實際渲染的揮手→驚嚇動畫）。
