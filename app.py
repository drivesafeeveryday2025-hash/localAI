import os
import shutil
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components
from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

from config import (
    RESOURCE_DIR,
    LLM_MODEL,
    EMBEDDING_MODEL,
    DEFAULT_TOP_K,
    configure_windows_encoding
)
from retriever import get_vector_store, get_retriever, check_ollama_alive
from ingest import ingest_single_file
from components.hero_3d import get_hero_3d_html
from components.pallet_3d import get_pallet_3d_html

configure_windows_encoding()

# Overall Page Configuration
st.set_page_config(
    page_title="Stanley AI 智慧大腦平台",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-Tech CSS Styling
st.markdown("""
<style>
    /* Gradient Accent Titles */
    .hero-title {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #38bdf8 0%, #818cf8 50%, #c084fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.2rem;
        letter-spacing: -0.5px;
    }
    .hero-subtitle {
        text-align: center;
        color: #94a3b8;
        font-size: 1.1rem;
        margin-bottom: 1.2rem;
    }
    /* Feature metric card */
    .metric-card {
        background: rgba(15, 23, 42, 0.65);
        border: 1px solid rgba(56, 189, 248, 0.25);
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
    }
    .metric-title {
        color: #38bdf8;
        font-size: 0.9rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .metric-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #f8fafc;
        margin: 0.4rem 0;
    }
    /* Card box inside calculator */
    .calc-card {
        background: rgba(15, 23, 42, 0.7);
        border: 1px solid rgba(148, 163, 184, 0.2);
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)


# ==============================================================================
# VIEW 1: 3D ENTRY / LANDING PAGE (Inspired by gfnnet.com)
# ==============================================================================
def home_view():
    st.markdown('<div class="hero-title">🌌 Stanley AI 智慧大腦平台</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Next-Gen Local RAG Knowledge Engine with Interactive 3D Holographic Core</div>', unsafe_allow_html=True)

    # Embed 3D Canvas (Draggable & Rotatable WebGL with Three.js)
    components.html(get_hero_3d_html(), height=540, scrolling=False)

    # Action Buttons: Chat, 3D Pallet, and Knowledge Editor
    col_btn1, col_btn2, col_btn3 = st.columns(3)
    with col_btn1:
        if st.button("🚀 進入 AI 智能問答系統 (Chat)", type="primary", use_container_width=True):
            st.switch_page(chat_page)
    with col_btn2:
        if st.button("📦 進入 3D 空間與棧板計算器 (Pallet)", type="secondary", use_container_width=True):
            st.switch_page(calc_page)
    with col_btn3:
        if st.button("📝 進入知識庫文檔編輯器 (Editor)", type="secondary", use_container_width=True):
            st.switch_page(editor_page)

    st.write("")
    st.divider()

    # System Overview Metrics Grid
    c1, c2, c3 = st.columns(3)
    
    with c1:
        all_docs = [f for f in RESOURCE_DIR.rglob("*") if f.is_file() and f.suffix.lower() in [".md", ".txt", ".pdf"]] if RESOURCE_DIR.exists() else []
        doc_count = len(all_docs)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">📁 知識庫文檔 (Documents)</div>
            <div class="metric-value">{doc_count} 份已就緒</div>
            <span style="color:#94a3b8; font-size: 0.85rem;">存放於 <code>./resource/</code> (含子分類目錄)</span>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        vs = get_vector_store()
        chunk_count = vs._collection.count()
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">⚡ 向量數據庫 (ChromaDB)</div>
            <div class="metric-value">{chunk_count} 個知識切片</div>
            <span style="color:#94a3b8; font-size: 0.85rem;">語意空間維度向量索引</span>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        status_text = "🟢 正常運行中" if check_ollama_alive() else "🔴 服務離線"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">🧠 本機大模型引擎</div>
            <div class="metric-value">{LLM_MODEL}</div>
            <span style="color:#94a3b8; font-size: 0.85rem;">{status_text} (Ollama 本地推理)</span>
        </div>
        """, unsafe_allow_html=True)

    # Ingested Files Details
    st.write("")
    with st.expander("📄 點擊查看目前已載入的知識庫文件列表 (包含所有分類子資料夾)"):
        if RESOURCE_DIR.exists():
            docs = [f for f in RESOURCE_DIR.rglob("*") if f.is_file() and f.suffix.lower() in [".md", ".txt", ".pdf"]]
            if docs:
                for f in sorted(docs):
                    rel = f.relative_to(RESOURCE_DIR).as_posix()
                    st.markdown(f"- 📄 **`{rel}`** ({round(f.stat().st_size / 1024, 2)} KB)")
            else:
                st.info("尚未檢測到任何知識庫文件")
        else:
            st.info("尚未檢測到 `resource/` 目錄")


# ==============================================================================
# VIEW 2: INTERACTIVE CHAT ASSISTANT
# ==============================================================================
def chat_view():
    top_col1, top_col2 = st.columns([4, 1.2])
    with top_col1:
        st.title("🤖 Local AI Knowledge Assistant")
        st.caption(f"Powered by LangChain + Ollama ({LLM_MODEL} & {EMBEDDING_MODEL}) + ChromaDB")
    with top_col2:
        st.write("")
        if st.button("🏠 返回 3D 首頁", use_container_width=True):
            st.switch_page(home_page)

    is_ollama_online = check_ollama_alive()
    if not is_ollama_online:
        st.error("⚠️ 無法連線至本地 Ollama (localhost:11434)。請先在終端機啟動服務：`ollama serve`")

    with st.sidebar:
        st.header("⚙️ 系統狀態與設定")
        status_badge = "🟢 線上" if is_ollama_online else "🔴 離線"
        st.markdown(f"**Ollama 服務狀態:** {status_badge}")
        st.markdown(f"**問答大模型:** `{LLM_MODEL}`")
        st.markdown(f"**嵌入模型:** `{EMBEDDING_MODEL}`")
        
        st.divider()
        st.subheader("📂 知識庫文件 (`resource/`)")
        if RESOURCE_DIR.exists():
            files = [f for f in RESOURCE_DIR.rglob("*") if f.is_file() and f.suffix.lower() in [".md", ".txt", ".pdf"]]
            if files:
                for f in sorted(files):
                    rel = f.relative_to(RESOURCE_DIR).as_posix()
                    st.markdown(f"- 📄 `{rel}`")
            else:
                st.info("`resource/` 目錄中暫無文件")
        else:
            st.warning("`resource/` 目錄未建立")

        vs = get_vector_store()
        total_chunks = vs._collection.count()
        st.caption(f"數據庫總切片數: **{total_chunks}**")

        st.divider()
        top_k = st.slider("每次查詢檢索切片數 (Top-K):", min_value=1, max_value=8, value=DEFAULT_TOP_K)
        
        if st.button("🗑️ 清空對話記錄", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

        st.divider()
        c_side1, c_side2 = st.columns(2)
        with c_side1:
            if st.button("🌐 返回首頁", use_container_width=True):
                st.switch_page(home_page)
        with c_side2:
            if st.button("📝 文檔編輯", use_container_width=True):
                st.switch_page(editor_page)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if "sources" in msg and msg["sources"]:
                with st.expander("📚 引用來源 (Sources Cited)"):
                    for src in msg["sources"]:
                        st.markdown(src)

    if user_prompt := st.chat_input("請輸入關於知識庫文件的問題 (例如：2011年銷售冠軍車款是什麼？)..."):
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.markdown(user_prompt)

        with st.chat_message("assistant"):
            custom_retriever = get_retriever(k=top_k)
            docs = custom_retriever.invoke(user_prompt)
            
            model = OllamaLLM(model=LLM_MODEL)
            template = """
You are an expert answering questions based strictly on the provided context.

Context:
{reviews}

Question:
{question}
"""
            prompt = ChatPromptTemplate.from_template(template)
            chain = prompt | model

            response_stream = chain.stream({"reviews": docs, "question": user_prompt})
            full_answer = st.write_stream(response_stream)

            source_records = []
            for i, doc in enumerate(docs, start=1):
                src_name = doc.metadata.get("source", "未知來源")
                preview = doc.page_content[:150].replace("\n", " ").strip()
                source_records.append(f"**[{i}] {src_name}**  \n> {preview}...")

            if source_records:
                with st.expander("📚 引用來源 (Sources Cited)"):
                    for src in source_records:
                        st.markdown(src)

        st.session_state.messages.append({
            "role": "assistant",
            "content": full_answer,
            "sources": source_records
        })


# ==============================================================================
# VIEW 3: 3D SPACE & PALLET SIMULATOR (3D 空間與棧板裝載計算器)
# ==============================================================================
def calc_view():
    top_col1, top_col2 = st.columns([4, 1.2])
    with top_col1:
        st.title("📦 3D 空間與棧板計算器")
        st.caption("3D Space, Pallet & Storage Room Box Stacking Simulator with Real-Time Math")
    with top_col2:
        st.write("")
        if st.button("🏠 返回 3D 首頁", use_container_width=True):
            st.switch_page(home_page)

    left_col, right_col = st.columns([1.1, 1.9], gap="large")

    with left_col:
        st.subheader("⚙️ 參數輸入與即時計算")

        # 1. Product Dimensions
        with st.expander("📦 單件商品尺寸 (Product Dimensions)", expanded=True):
            p_col1, p_col2, p_col3 = st.columns(3)
            with p_col1:
                item_l = st.number_input("長度 (Length) [m]", min_value=0.05, value=0.40, step=0.05, format="%.2f")
            with p_col2:
                item_w = st.number_input("寬度 (Width) [m]", min_value=0.05, value=0.30, step=0.05, format="%.2f")
            with p_col3:
                item_h = st.number_input("高度 (Height) [m]", min_value=0.05, value=0.25, step=0.05, format="%.2f")

            # Dynamic Product Volume
            item_vol = round(item_l * item_w * item_h, 4)
            st.info(f"📐 **商品單件體積 (Volume)**: `{item_vol} m³` ({round(item_vol * 1000, 1)} L)")

        # 2. Target Container Choice
        target_choice = st.selectbox(
            "🎯 選擇目標存放容器 (Target Container):",
            ["Pallet (棧板裝載)", "Storage Room (倉庫儲藏室)"]
        )

        # 3. Container Dimensions
        if target_choice == "Pallet (棧板裝載)":
            target_type_key = "Pallet"
            with st.expander("🪵 棧板規格與限高 (Pallet Specifications)", expanded=True):
                c1, c2, c3 = st.columns(3)
                with c1:
                    p_l = st.number_input("棧板長度 (pLength) [m]", min_value=0.2, value=1.20, step=0.1, format="%.2f")
                with c2:
                    p_w = st.number_input("棧板寬度 (pWidth) [m]", min_value=0.2, value=1.00, step=0.1, format="%.2f")
                with c3:
                    p_h = st.number_input("堆疊限高 (pHeight) [m]", min_value=0.2, value=1.50, step=0.1, format="%.2f")

                pallet_vol = round(p_l * p_w * p_h, 3)
                pallet_area = round(p_l * p_w, 2)
                st.success(f"📊 **棧板容積**: `{pallet_vol} m³` | **底面積**: `{pallet_area} m²`")
                
                c_len, c_wid, c_hei = p_l, p_w, p_h
                c_vol = pallet_vol

        else:
            target_type_key = "Storage Room"
            with st.expander("🏢 倉庫儲藏室規格 (Storage Room Specifications)", expanded=True):
                c1, c2, c3 = st.columns(3)
                with c1:
                    s_l = st.number_input("倉庫長度 (sLength) [m]", min_value=1.0, value=6.00, step=0.5, format="%.2f")
                with c2:
                    s_w = st.number_input("倉庫寬度 (sWidth) [m]", min_value=1.0, value=4.00, step=0.5, format="%.2f")
                with c3:
                    s_h = st.number_input("倉庫高度 (sHeight) [m]", min_value=1.0, value=3.00, step=0.5, format="%.2f")

                room_vol = round(s_l * s_w * s_h, 2)
                room_area = round(s_l * s_w, 2)
                st.success(f"📊 **倉庫容積 (Volume)**: `{room_vol} m³` | **地面積**: `{room_area} m²`")

                c_len, c_wid, c_hei = s_l, s_w, s_h
                c_vol = room_vol

        # 4. Maximum Packing Quantity Calculation
        fit_l = max(1, int(c_len // item_l))
        fit_w = max(1, int(c_wid // item_w))
        fit_h = max(1, int(c_hei // item_h))
        max_capacity = fit_l * fit_w * fit_h

        st.markdown(f"""
        <div class="calc-card">
            <div style="font-size: 0.85rem; color: #38bdf8; font-weight: 600;">理論最大可裝載數量 (Max Packing Capacity)</div>
            <div style="font-size: 1.8rem; font-weight: 800; color: #f8fafc; margin: 0.3rem 0;">{max_capacity:,} 件</div>
            <span style="color: #94a3b8; font-size: 0.85rem;">長向 <b>{fit_l}</b> 排 × 寬向 <b>{fit_w}</b> 排 × 高向 <b>{fit_h}</b> 層</span>
        </div>
        """, unsafe_allow_html=True)

        # 5. Quantity Input & Quick Fill
        col_q1, col_q2 = st.columns([2.5, 1.5])
        with col_q1:
            if "target_qty" not in st.session_state:
                st.session_state.target_qty = min(max_capacity, 36)

            # Ensure session state doesn't exceed new max_capacity
            if st.session_state.target_qty > max_capacity:
                st.session_state.target_qty = max_capacity

            qty_input = st.number_input(
                "欲裝載數量 (Quantity):",
                min_value=1,
                max_value=max(1, max_capacity),
                value=st.session_state.target_qty,
                step=1
            )
        with col_q2:
            st.write("")
            st.write("")
            if st.button("⚡ 填滿最大量", use_container_width=True):
                st.session_state.target_qty = max_capacity
                st.rerun()

        # Space Utilization Progress
        utilization = round((qty_input * item_vol / c_vol) * 100, 1) if c_vol > 0 else 0
        st.progress(min(1.0, utilization / 100.0), text=f"空間利用率 (Space Utilization): {utilization}%")

    with right_col:
        st.subheader("🌐 3D 空間裝載視覺化 (3D Packing Simulator)")
        
        # Render 3D WebGL Packing Viewport
        html_code = get_pallet_3d_html(
            target_type=target_type_key,
            item_l=item_l,
            item_w=item_w,
            item_h=item_h,
            container_l=c_len,
            container_w=c_wid,
            container_h=c_hei,
            quantity=qty_input,
            max_quantity=max_capacity,
            utilization=utilization
        )
        components.html(html_code, height=620, scrolling=False)

        # Breakdown summary pill tags below canvas
        pills_c1, pills_c2, pills_c3 = st.columns(3)
        with pills_c1:
            st.caption(f"📏 容器規格: **{c_len}m × {c_wid}m × {c_hei}m**")
        with pills_c2:
            st.caption(f"📦 單箱規格: **{item_l}m × {item_w}m × {item_h}m**")
        with pills_c3:
            st.caption(f"📊 實際總貨量體積: **{round(qty_input * item_vol, 3)} m³**")


# ==============================================================================
# VIEW 4: KNOWLEDGE BASE DOCUMENT EDITOR (知識庫文檔編輯器)
# ==============================================================================
def editor_view():
    top_col1, top_col2 = st.columns([4, 1.2])
    with top_col1:
        st.title("📝 知識庫文檔編輯器 (Document Knowledge Editor)")
        st.caption("自訂分類子資料夾、豐富文字樣式排版（字體大小、顏色、底線、粗細、背景色），一鍵存檔並即時同步 ChromaDB 向量庫")
    with top_col2:
        st.write("")
        if st.button("🏠 返回 3D 首頁", use_container_width=True):
            st.switch_page(home_page)

    # Session State Initialization for Editor
    if "editor_category" not in st.session_state:
        st.session_state.editor_category = "汽車"
    if "editor_custom_cat" not in st.session_state:
        st.session_state.editor_custom_cat = ""
    if "editor_title" not in st.session_state:
        st.session_state.editor_title = ""
    if "editor_content" not in st.session_state:
        st.session_state.editor_content = ""

    # Two columns: Left for Document Editing & Styling, Right for Directory Tree Menu
    left_editor, right_tree = st.columns([1.75, 1.25], gap="large")

    with right_tree:
        st.subheader("📂 知識庫目錄樹 (Folder Structure)")
        st.caption("即時掃描 `./resource/` 包含所有子資料夾之檔案")

        # Scan resource directory
        if not RESOURCE_DIR.exists():
            RESOURCE_DIR.mkdir(parents=True, exist_ok=True)

        all_files = [f for f in RESOURCE_DIR.rglob("*") if f.is_file() and f.suffix.lower() in [".md", ".txt", ".pdf"]]
        
        # Quick stats
        total_files = len(all_files)
        total_size_kb = round(sum(f.stat().st_size for f in all_files) / 1024, 2)
        st.markdown(f"""
        <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(56, 189, 248, 0.25); border-radius: 8px; padding: 0.7rem; margin-bottom: 0.8rem; font-size: 0.85rem;">
            📊 總文件數：<b>{total_files}</b> 篇 | 佔用空間：<b>{total_size_kb} KB</b>
        </div>
        """, unsafe_allow_html=True)

        # Group files by relative folder
        grouped_files = {}
        for f in all_files:
            rel_parent = f.relative_to(RESOURCE_DIR).parent.as_posix()
            folder_key = "根目錄 (root)" if rel_parent == "." else rel_parent
            if folder_key not in grouped_files:
                grouped_files[folder_key] = []
            grouped_files[folder_key].append(f)

        # Render directory tree
        if not grouped_files:
            st.info("目前 `resource/` 尚無文檔，可透過左側編輯器建立第一篇文檔！")
        else:
            for folder, files in sorted(grouped_files.items()):
                with st.expander(f"📁 **{folder}** ({len(files)} 篇)", expanded=True):
                    for file_item in sorted(files, key=lambda x: x.name):
                        col_info, col_load, col_del = st.columns([2.0, 0.9, 0.5])
                        file_size_kb = round(file_item.stat().st_size / 1024, 2)
                        with col_info:
                            st.markdown(f"📄 **{file_item.name}**  \n<span style='font-size:0.75rem; color:#94a3b8;'>{file_size_kb} KB</span>", unsafe_allow_html=True)
                        with col_load:
                            if st.button("📖 載入", key=f"load_{file_item.relative_to(RESOURCE_DIR)}", use_container_width=True):
                                try:
                                    with open(file_item, "r", encoding="utf-8") as rf:
                                        loaded_text = rf.read()
                                    rel_p = file_item.relative_to(RESOURCE_DIR).parent.as_posix()
                                    st.session_state.editor_category = "" if rel_p == "." else rel_p
                                    st.session_state.editor_custom_cat = "" if rel_p == "." else rel_p
                                    st.session_state.editor_title = file_item.stem
                                    st.session_state.editor_content = loaded_text
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"載入失敗: {e}")
                        with col_del:
                            if st.button("🗑️", key=f"del_{file_item.relative_to(RESOURCE_DIR)}", help="刪除此檔案", use_container_width=True):
                                try:
                                    file_item.unlink()
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"刪除失敗: {e}")

        st.divider()
        st.markdown("""
        <div style="background: rgba(56, 189, 248, 0.08); border-left: 3px solid #38bdf8; padding: 0.6rem 0.8rem; border-radius: 4px; font-size: 0.82rem; color: #cbd5e1;">
            💡 <b>子資料夾階層支援</b>：Stanley AI 智慧大腦全面採用 <code>rglob("*")</code> 遞迴檢索。無論文檔存放於多深的子目錄（如 <code>resource/汽車/2026/yaris.md</code>），系統皆能自動解析並提供 AI 問答精準引用！
        </div>
        """, unsafe_allow_html=True)

    with left_editor:
        st.subheader("✍️ 建立 / 編輯文檔 (Document Input)")

        # 1. Category and Title Inputs
        c_cat, c_tit = st.columns([1, 1.5])
        
        # Collect existing category folders
        existing_categories = ["➕ 新增自訂分類 (New Category)..."]
        if RESOURCE_DIR.exists():
            for d in RESOURCE_DIR.iterdir():
                if d.is_dir():
                    existing_categories.append(d.name)
        
        # Default options
        for default_cat in ["汽車", "物流倉儲", "硬體設備", "系統手冊"]:
            if default_cat not in existing_categories:
                existing_categories.append(default_cat)

        with c_cat:
            cat_index = 0
            if st.session_state.editor_category in existing_categories:
                cat_index = existing_categories.index(st.session_state.editor_category)
            
            selected_cat = st.selectbox("📂 選擇分類 (Category):", existing_categories, index=cat_index)
            
            if selected_cat == "➕ 新增自訂分類 (New Category)...":
                custom_cat = st.text_input("輸入新分類名稱 (可包含子層級如 `汽車/豐田`):", value=st.session_state.editor_custom_cat, placeholder="例: 智慧物流")
                final_category = custom_cat.strip()
            else:
                final_category = selected_cat

        with c_tit:
            doc_title = st.text_input("📌 文件標題 (Title):", value=st.session_state.editor_title, placeholder="例: 2026 Toyota Yaris 規格指南")

        # 2. Rich Styling Toolbar
        with st.expander("🎨 豐富文字排版樣式工具箱 (Rich Styling Toolbar)", expanded=True):
            st.caption("可調整字體大小、顏色、粗細、底線與背景色，產生樣式標籤或插入至文檔中：")
            
            # Row 1: Font Size, Weight, Underline
            st_col1, st_col2, st_col3 = st.columns([1.2, 1.2, 1])
            with st_col1:
                font_size = st.selectbox(
                    "📏 字體大小 (Size):",
                    [
                        "預設大小 (Default - 1.0rem)",
                        "小標註 (Small - 0.85rem)",
                        "強調加大 (Medium - 1.2rem)",
                        "三級標題 (H3 - 1.4rem)",
                        "次級標題 (H2 - 1.8rem)",
                        "頂級大標題 (H1 - 2.4rem)"
                    ],
                    index=2
                )
            with st_col2:
                font_weight = st.selectbox(
                    "🏋️ 字體粗細 (Weight):",
                    [
                        "正常 (Normal - 400)",
                        "半粗體 (Semi-Bold - 600)",
                        "粗體 (Bold - 700)",
                        "特粗黑體 (Extra-Bold - 900)"
                    ],
                    index=2
                )
            with st_col3:
                is_underline = st.checkbox("🏷️ 加底線 (Underline)", value=False)

            # Row 2: Font Color & Background Color
            st_col4, st_col5 = st.columns(2)
            with st_col4:
                color_presets = {
                    "科技亮藍 (#38bdf8)": "#38bdf8",
                    "雪白 (#f8fafc)": "#f8fafc",
                    "翡翠亮綠 (#4ade80)": "#4ade80",
                    "活力暖橙 (#fb923c)": "#fb923c",
                    "炫彩紫 (#c084fc)": "#c084fc",
                    "鮮豔薔薇紅 (#f87171)": "#f87171",
                    "明亮金黃 (#facc15)": "#facc15"
                }
                chosen_color_name = st.selectbox("🎨 字體顏色 (Font Color):", list(color_presets.keys()), index=0)
                custom_font_color = st.color_picker("或自選顏色碼:", color_presets[chosen_color_name])

            with st_col5:
                bg_presets = {
                    "螢光黃高亮 (Yellow Highlight)": "rgba(250, 204, 21, 0.25)",
                    "無背景色 (Transparent)": "transparent",
                    "科技藍微光 (Blue Tint)": "rgba(56, 189, 248, 0.15)",
                    "翡翠綠徽章 (Green Tint)": "rgba(74, 222, 128, 0.2)",
                    "炫彩紫高光 (Purple Tint)": "rgba(192, 132, 252, 0.2)",
                    "警示紅標記 (Red Warning)": "rgba(248, 113, 113, 0.2)",
                    "深灰底卡片 (Dark Card)": "rgba(15, 23, 42, 0.8)"
                }
                chosen_bg_name = st.selectbox("🖍️ 字體背景高亮色 (Background):", list(bg_presets.keys()), index=0)
                custom_bg_color = bg_presets[chosen_bg_name]

            # Snippet Generator Helper
            st.divider()
            snip_col1, snip_col2 = st.columns([2.5, 1.2])
            with snip_col1:
                snippet_text = st.text_input("✍️ 欲樣式化之文字 (Snippet text):", value="2026 Toyota Yaris D-CVT 性能旗艦", placeholder="輸入想要加上樣式的文字...")
            
            # Resolve CSS parameters
            size_val_map = {
                "預設大小 (Default - 1.0rem)": "1.0rem",
                "小標註 (Small - 0.85rem)": "0.85rem",
                "強調加大 (Medium - 1.2rem)": "1.2rem",
                "三級標題 (H3 - 1.4rem)": "1.4rem",
                "次級標題 (H2 - 1.8rem)": "1.8rem",
                "頂級大標題 (H1 - 2.4rem)": "2.4rem"
            }
            weight_val_map = {
                "正常 (Normal - 400)": "400",
                "半粗體 (Semi-Bold - 600)": "600",
                "粗體 (Bold - 700)": "700",
                "特粗黑體 (Extra-Bold - 900)": "900"
            }
            css_size = size_val_map.get(font_size, "1.2rem")
            css_weight = weight_val_map.get(font_weight, "700")
            css_underline = "underline" if is_underline else "none"
            css_style_str = f"font-size: {css_size}; color: {custom_font_color}; font-weight: {css_weight}; text-decoration: {css_underline}; background-color: {custom_bg_color}; padding: 3px 8px; border-radius: 6px; display: inline-block;"

            # Live preview of snippet
            st.markdown(f"**樣式即時效果：** <span style='{css_style_str}'>{snippet_text}</span>", unsafe_allow_html=True)
            html_snippet = f"<span style=\"{css_style_str}\">{snippet_text}</span>"

            with snip_col2:
                st.write("")
                if st.button("➕ 插入至內容", use_container_width=True):
                    if st.session_state.editor_content:
                        st.session_state.editor_content += f"\n\n{html_snippet}\n\n"
                    else:
                        st.session_state.editor_content = f"{html_snippet}\n\n"
                    st.rerun()

        # 3. Content Text Area
        doc_content = st.text_area(
            "📄 文件內容 (Content - 支援 Markdown、純文字與 HTML 樣式標籤):",
            value=st.session_state.editor_content,
            height=280,
            placeholder="在此輸入文檔內容...\n例如：\n# 產品概觀\n這是一段支援樣式標籤的豐富說明。"
        )
        # Update session state content
        st.session_state.editor_content = doc_content
        st.session_state.editor_title = doc_title
        st.session_state.editor_category = final_category

        # 4. Live Rendered Preview
        with st.expander("👁️ 即時文件渲染預覽 (Live Styled Preview)", expanded=True):
            if doc_content.strip():
                st.markdown(f"### {doc_title if doc_title else '（未命名標題）'}")
                st.caption(f"分類：`{final_category if final_category else '根目錄'}`")
                st.markdown(doc_content, unsafe_allow_html=True)
            else:
                st.info("於上方輸入內容後，此處將即時呈現帶有字體大小、顏色、底線、粗細與背景色的精美預覽效果。")

        # 5. Save & Sync Action
        st.write("")
        col_save, col_clear = st.columns([2, 1])
        with col_save:
            if st.button("💾 儲存文檔並即時同步至 ChromaDB (Save & Sync)", type="primary", use_container_width=True):
                if not doc_title.strip():
                    st.error("❌ 請輸入『文件標題』後再儲存！")
                elif not doc_content.strip():
                    st.error("❌ 請輸入『文件內容』後再儲存！")
                else:
                    # Sanitize filename
                    safe_title = "".join(c for c in doc_title.strip() if c.isalnum() or c in (" ", "_", "-", "（", "）", "(", ")")).strip()
                    if not safe_title:
                        safe_title = "untitled_doc"
                    filename = f"{safe_title}.md"

                    # Determine target directory
                    if final_category:
                        clean_cat = final_category.strip("/\\ ")
                        target_dir = RESOURCE_DIR / clean_cat
                    else:
                        target_dir = RESOURCE_DIR
                    
                    target_dir.mkdir(parents=True, exist_ok=True)
                    target_file = target_dir / filename

                    try:
                        # Save file with UTF-8 encoding
                        target_file.write_text(doc_content, encoding="utf-8")
                        
                        # Ingest into ChromaDB immediately!
                        chunks_added = ingest_single_file(target_file)

                        st.success(f"🎉 檔案已成功儲存至 `{target_file.relative_to(RESOURCE_DIR).as_posix()}`！")
                        st.info(f"⚡ ChromaDB 向量資料庫已即時同步：新增 **{chunks_added}** 個切片，對話助手可立即檢索此文檔！")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ 儲存或向量化失敗: {e}")

        with col_clear:
            if st.button("🧹 清空編輯器", use_container_width=True):
                st.session_state.editor_category = "汽車"
                st.session_state.editor_custom_cat = ""
                st.session_state.editor_title = ""
                st.session_state.editor_content = ""
                st.rerun()


# ==============================================================================
# STREAMLIT MULTI-PAGE NAVIGATION SETUP
# ==============================================================================
home_page = st.Page(home_view, title="3D 首頁 (Home)", icon="🌌", default=True)
chat_page = st.Page(chat_view, title="智能問答 (Chat Assistant)", icon="💬")
calc_page = st.Page(calc_view, title="3D 空間與棧板計算器 (Simulator)", icon="📦")
editor_page = st.Page(editor_view, title="知識庫編輯器 (Document Editor)", icon="📝")

pg = st.navigation([home_page, chat_page, calc_page, editor_page])
pg.run()
