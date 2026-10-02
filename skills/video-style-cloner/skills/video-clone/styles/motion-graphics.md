---
name: motion-graphics
engine: hyperframes
medium: 2d-vector
priority: 60
---
# 動態圖像 / 字卡動畫（kinetic typography、數據、Logo 片頭）

## 辨識特徵
- 畫面：乾淨向量、大字標題、圖表、UI 元件、幾何圖形，常見漸層或品牌色
- 剪接：快節奏、字與圖形跟著拍點進場，轉場多為推移、縮放、遮罩
- 聲音：純音樂或音效，通常無旁白、短（< 30 秒）
- 文字：文字本身就是主角

## 製作預設
- 走 `/hyperframes` 路由 → `/motion-graphics`（短、無旁白）或 `/general-video`（較長、多段）
- 動態規則先讀 `/motion-doctrine`（轉場向量連貫），轉場效果先查 `/hyperframes-registry`

## 已知的坑
- HyperFrames CLI：`npx hyperframes@latest init <name> --non-interactive`；環境變數 HYPERFRAMES_NO_TELEMETRY=1 已在 settings 設好
