# 🌌 Stanley AI 智慧大腦平台 (Stanley AI Platform)

> **次世代本機端 RAG 智慧知識庫檢索系統 × 3D 空間與棧板裝載模擬平台**  
> Next-Generation Local RAG Knowledge Engine & Interactive 3D Holographic Simulation Platform.

---

## 🌟 核心功能特色 (Features)

### 1. 🌐 3D 全息互動首頁 (3D Holographic Core)
- 基於 **Three.js** 與 **WebGL** 原生渲染技術，無需下載額外 3D 模型檔。
- 具備 360° 滑鼠拖曳旋轉、縮放視角的全息物流複合體（堆高機、運輸貨車、工程工作站、全息懸浮光球與 2D 資訊標籤）。

### 2. 💬 本地端隱私 AI 智能問答 (Local RAG Chat Assistant)
- **100% 離線隱私保護**：採用 **Ollama** 本地大模型推理 (`qwen2.5-coder`) 與高效向量嵌入 (`mxbai-embed-large`)。
- **即時文字串流**：支援逐字打字機效果 (`st.write_stream`)。
- **精準引用來源**：每次回答均附帶可折疊的參考文獻來源與內文摘要抽屜。

### 3. 📦 3D 空間與棧板計算器 (3D Space & Pallet Simulator)
- **即時幾何計算**：輸入商品長寬高，即時換算單件體積 ($m^3$ 與 $L$)。
- **多容器支援**：可切換 **Pallet (棧板)** 或 **Storage Room (倉庫儲藏室)** 規格。
- **最大容量公式運算**：自動計算正交排列下的理論最大裝載量與空間利用率。
- **3D 即時裝載視覺化**：自訂裝載數量或點擊「填滿最大量」，3D 視窗即時動態堆疊排列紙箱，支援 360° 旋轉檢視。

### 4. 📝 知識庫文檔編輯器 (Document Knowledge Editor)
- **自訂分類子資料夾**：支援深層分類結構（如 `汽車/國產`、`倉儲物流`）。
- **豐富文字排版樣式工具箱 (Rich Typography Toolbar)**：
  - 字體大小（小標註至頂級大標題）
  - 字體顏色（科技藍、雪白、翡翠綠、暖橙、炫彩紫、薔薇紅等或自選調色盤）
  - 字體粗細（400 ~ 900）
  - 字體底線裝飾
  - 字體背景高亮色（螢光黃高亮、科技藍微光、翡翠綠徽章、警示紅等）
- **即時排版渲染預覽**：所見即所得，支援 Markdown 與 inline HTML 樣式。
- **即時增量同步 ChromaDB**：存檔同時呼叫 `ingest_single_file`，毫秒級完成向量化，對話助手免重啟立即查得到。
- **目錄樹瀏覽器 (Directory Tree Browser)**：清楚檢視 `resource/` 下所有分類檔案與大小，支援一鍵載入與刪除。
- **無限層級子資料夾遞迴搜尋**：全系統採用 `rglob("*")`，不限子目錄深度自動檢索。

---

## 🛠️ 技術架構 (Tech Stack)

| 組件 | 技術 / 框架 | 說明 |
| :--- | :--- | :--- |
| **語言** | Python 3.10+ | 核心開發語言 |
| **Web 前端框架** | Streamlit | 現代化多頁面儀表板與互動介面 |
| **3D 視覺渲染** | Three.js (WebGL) | 輕量化、零外部資源依賴之 3D 場景與堆疊模擬 |
| **RAG 編排框架** | LangChain | 文檔切片、檢索器建立與 Prompt 鏈結 |
| **本地大模型** | Ollama (`qwen2.5-coder`) | 高效能本地端問答生成模型 |
| **向量嵌入模型** | Ollama (`mxbai-embed-large`) | 語意空間高維度向量表徵 |
| **向量資料庫** | ChromaDB | 本地持久化嵌入向量索引數據庫 |

---

## 📁 專案目錄結構 (Directory Tree)

```
d:/AI/
├── components/                           # Web UI 3D 視覺組件
│   ├── hero_3d.py                        # Three.js 全息物流複合體
│   └── pallet_3d.py                      # Three.js 棧板與空間裝載堆疊模擬器
├── resource/                             # 知識庫文檔放置目錄 (已加入 .gitignore 保障隱私，不進行版本控制)
│   └── (於本機存放您的 .txt / .md 私有知識文檔，支援任意分類子目錄)
├── plan/                                 # 內部規劃與開發進程紀錄 (已加入 .gitignore，不進行版本控制)
├── venv/                                 # Python 虛擬環境 (已加入 .gitignore)
├── config.py                             # 全域集中設定檔 (路徑、模型、文字切片參數)
├── ingest.py                             # 遞迴文檔切片與 ChromaDB 向量化管道
├── retriever.py                          # 輕量級向量庫查詢介面與連線健康檢查
├── main.py                               # 終端機互動式問答命令列介面 (CLI)
├── app.py                                # Streamlit 多頁面 Web 應用程式
├── requirements.txt                      # 專案 Python 相依套件清單
└── README.md                             # 專案說明文件
```

---

## 🚀 快速開始指南 (Quick Start)

### 1. 安裝環境需求
- **Python 3.10+**
- **Ollama**: [https://ollama.com](https://ollama.com)

### 2. 下載本地 AI 模型
在命令提示字元或 PowerShell 中執行：
```powershell
ollama pull qwen2.5-coder
ollama pull mxbai-embed-large
```

### 3. 建立並啟用虛擬環境
```powershell
# 建立虛擬環境
python -m venv venv

# 啟用虛擬環境 (Windows PowerShell)
.\venv\Scripts\Activate.ps1
```

### 4. 安裝相依套件
```powershell
pip install -r requirements.txt
```

### 5. 向量資料庫建立 (Ingestion)
將您的 Markdown (`.md`) 或文字檔 (`.txt`) 放入 `resource/` 目錄（或子資料夾），然後執行：
```powershell
python ingest.py
```

### 6. 啟動平台
#### 🌟 方式 A：啟動 Streamlit 3D 整合平台 (推薦)
```powershell
streamlit run app.py
```
啟動後瀏覽器會自動開啟 `http://localhost:8501`。

#### 💻 方式 B：啟動終端機互動式問答 (CLI)
```powershell
python main.py
```

---

## 📄 授權條款 (License)

This project is developed for internal enterprise knowledge retrieval and logistics simulation.  
Created by Stanley.

