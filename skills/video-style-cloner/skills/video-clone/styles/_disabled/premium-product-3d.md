---
name: premium-product-3d
engine: blender-product-film
medium: 3d-photoreal
priority: 90
---
# 高級 3D 產品片（黑場、輪廓光、微距、材質證明）

## 辨識特徵
- 畫面：擬真 3D 渲染或棚拍質感的產品特寫；黑色／深色舞台、單側或輪廓光、光線掃過材質；玻璃、金屬、液體等材質細節
- 運鏡：幾乎每個鏡頭都在動，以慢速推近／拉遠、環繞、微距平移為主（analyze.py 的 shot_details：moving_camera_shots 高、pace 多為 slow/medium）
- 剪接：平均鏡頭 1.5–4 秒，段落之間常經過黑場；標語字卡穿插（黑底白字、灰白兩階、逐字點亮）
- 敘事：揭曉 → 逐項證明（每個賣點一個視覺證明）→ 回到英雄鏡頭謝幕 → 品名
- 範例：手機、耳機、手錶、飲料瓶、香水的官方發表片

## 製作預設
- engine：`blender-product-film`（Blender Cycles + GPU）。使用者提供產品照片 → `prep_product.py` 從照片重建產品（真實輪廓 + 標籤投影）
- 1920×1080、30 fps、依參考片長度（預設 30–40 秒）
- 企劃必須逐鏡對照參考片：每個鏡頭填 `ref_shot`（參考片鏡頭編號）與 `camera`（move、lens、fill、region、dof、速度），運鏡種類與速度要和參考鏡頭一致
- 產品在畫面中要大：英雄鏡頭 fill ≥ 0.7；細節鏡頭用 region + fill ≥ 0.8
- 標題在後期 2D 疊上（finish.py），放在留白處，不壓產品；純字卡時間 ≤ 全片 15–20%（依參考片比例）
- 真實品牌：只用產品上印的資訊或使用者給的資料當標語，不自編規格數字

## 已知的坑
- 見 blender-product-film/SKILL.md 的 Known pitfalls（EEVEE 透明折射黑邊、背光板淹沒畫面、地板反射燈箱、CJK 可變字型空白、小圖要超解析）
- 不要把 3D 參考片降級成 2D 向量：媒材不符時寧可回報做不到
