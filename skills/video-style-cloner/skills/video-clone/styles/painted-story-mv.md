---
name: painted-story-mv
engine: painted-animation
medium: 2d-painted
priority: 80
---
# 手繪水彩劇情 MV（一首歌帶一個小故事）

## 辨識特徵
- 畫面：扁平 2D、墨線會微微抖動（boil）、水彩填色與紙紋、角色是簡單幾何造型帶表情符號（! ? 汗滴 愛心）
- 剪接：一句歌詞 ≈ 一個鏡頭（常見 8 拍），每個接縫都有設計過的轉場（筆刷抹過、光圈、布幕、變形接續）
- 聲音：整首歌驅動節奏，沒有旁白
- 文字：除了卡拉 OK 字幕外幾乎沒有字；常有「歌詞諧音梗」的視覺笑點
- 範例：小鎮姑娘（painted-animation 的 examples/xiaozhen）、本專案 projects/zhainan

## 製作預設
- 1920×1080（直式需求改 1080×1920 構圖但引擎畫布固定 16:9 → 以鏡頭構圖置中、輸出後裁切）、24 fps、預設 30 秒
- **角色一律原創**：從 `../assets/cast_rig.js` 起手（rig() + 兩個範例角色 zhai()/hua() + 道具），複製到專案 `src/cast.js` 再改造型；
  不直接使用引擎內建角色或任何既有角色
- 所有時間用拍計：`const B = n => OFF + n * BEAT`，BPM/offset 由 analyze.py 的報告填進 `src/config.js`
- 分鏡格式：Logline / World+色彩弧線 / Motif / 情緒弧線 / 鏡頭表（拍數、轉場、事件、reads），結尾要呼應開場

## 已知的坑
- Windows：`scripts/new_project.sh` 需要 rsync → 改用 `cp -r <skill>/template <project>` + `npm install`（或從既有專案複製 node_modules）
- `emotions()` 會把 col/dk/lt 從引擎預設色開始混色 → cast_rig.js 的 rig() 已忽略這三個值（除非傳 `ownCol: true`）
- 引擎的 tint（flush/rosy/pale）是為橘色角色調的，套在其他底色會偏色 → 在 emotion key 裡加 `{ tintK: .25 }` 壓低
- 不要用引擎函式的名字當區域變數（例：`const hat = …` 會讓 `hat()` 失效，報 "hat is not a function"）
- 遠景角色容易太小：中景 u≈24–30 且相機 zoom ≥ 1.3；每次先出總覽 sheet 檢查
- 手持道具若畫在手臂 hook 裡會跟著手臂旋轉；需要保持直立的（雨傘）改畫在世界座標
- 超大（比畫布大很多）的 `fill` 形狀（天空、地面用 `fill` + `bleed`）在鏡頭 zoom < 1 時會在畫面中間畫出一條半透明的水彩邊帶狀雜訊 → 大面積底色只用 `wash`，要層次就疊幾塊較小的 `wash` 或用 `glow()`
- render.mjs `--frames --workers=6` 在 Windows 偶爾導覽逾時（字型載入）→ 用 `--workers=3`，失敗就重跑（會續跑）
