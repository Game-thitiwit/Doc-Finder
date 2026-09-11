import base64
from datetime import datetime
import io
import re
from urllib.parse import quote
import zipfile

import pandas as pd
import requests
import streamlit as st

# ==========================================
# 1. ตั้งค่า ID และ Apps Script Web App URL
# ==========================================
SPREADSHEET_ID = "18in_VjpzzydR-gonOAsd_vX2DaQYJWJVJJL0xQzI6So"
FOLDER_ID = "1DPOfNiU6UjLfBLcOWV8yFKGCmssFZwIQ"
APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbyOEsBcUxJUWaaEF2MPGn2n6CzlseWltb9-vzgnZ7UWZUMVfz-ljrW9zENfXyskUlRF/exec"

st.set_page_config(
    page_title="Doc Finder", page_icon="🗃️", layout="wide"
)

# ==========================================
# 2. Premium Custom CSS (Design System + 3D Effects)
# ==========================================
CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;500;600;700&display=swap');

    :root {
        --primary-gradient: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
        --glass-bg: rgba(255, 255, 255, 0.7);
        --glass-border: rgba(255, 255, 255, 0.5);
        --shadow-soft: 0 8px 32px rgba(31, 38, 135, 0.07);
        --shadow-glow: 0 8px 24px rgba(124, 58, 237, 0.3);
        --text-main: #1E293B;
        --text-muted: #64748B;
        --border-radius: 20px;
        --transition-speed: 0.3s;
    }

    /* Dark Mode Auto-Adaptation */
    @media (prefers-color-scheme: dark) {
        :root {
            --glass-bg: rgba(15, 23, 42, 0.6);
            --glass-border: rgba(255, 255, 255, 0.08);
            --text-main: #F8FAFC;
            --text-muted: #94A3B8;
            --shadow-soft: 0 8px 32px rgba(0, 0, 0, 0.4);
        }
    }

    html, body, [class*="css"] {
        font-family: 'Prompt', sans-serif !important;
        color: var(--text-main);
    }

    /* Animations */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes floating {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-8px); }
        100% { transform: translateY(0px); }
    }

    .animate-fade-in {
        animation: fadeInUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }

    /* =========================================
       ✨ CONTROL PANEL (GLOW & SPINNING BORDER) ✨
       ========================================= */
    .sidebar-glow-panel {
        background: #0f172a;
        border-radius: 16px;
        padding: 3px; /* ความหนาของเส้นขอบไฟวิ่ง */
        position: relative;
        overflow: hidden;
        margin-bottom: 25px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3), inset 0 2px 5px rgba(255,255,255,0.2);
    }
    
    .sidebar-glow-panel::before {
        content: '';
        position: absolute;
        top: -50%; left: -50%; width: 200%; height: 200%;
        background: conic-gradient(from 0deg, transparent 0%, #3b82f6 25%, #8b5cf6 50%, transparent 50%);
        animation: spin-glow 3s linear infinite;
    }
    
    .sidebar-glow-panel .panel-content {
        background: linear-gradient(180deg, #1e293b, #0f172a);
        border-radius: 14px;
        padding: 15px;
        position: relative;
        z-index: 1;
        text-align: center;
        font-size: 1.4rem;
        font-weight: 700;
        color: white;
        text-shadow: 0 2px 4px rgba(0,0,0,0.5);
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 10px;
    }

    @keyframes spin-glow {
        100% { transform: rotate(360deg); }
    }

    /* =========================================
       🎮 3D BUTTONS & RUNNING LIGHT EFFECT 🎮
       ========================================= */
    div[data-testid="stButton"] > button,
    div[data-testid="stDownloadButton"] > button {
        position: relative !important;
        overflow: hidden !important;
        border: none !important;
        border-radius: 12px !important;
        color: white !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px !important;
        transition: all 0.1s cubic-bezier(0.4, 0, 0.2, 1) !important;
        z-index: 1 !important;
        text-transform: none !important;
    }

    /* 🔵 ปุ่มกดทั่วไป (Standard Buttons) */
    div[data-testid="stButton"] > button {
        background: linear-gradient(180deg, #6366f1 0%, #4338ca 100%) !important;
        box-shadow: 
            0 6px 0 #312e81, 
            0 10px 20px rgba(0,0,0,0.3), 
            inset 0 2px 2px rgba(255,255,255,0.4) !important;
    }
    div[data-testid="stButton"] > button:hover {
        filter: brightness(1.1) !important;
        transform: translateY(2px) !important;
        box-shadow: 
            0 4px 0 #312e81, 
            0 8px 15px rgba(0,0,0,0.3), 
            inset 0 2px 2px rgba(255,255,255,0.4) !important;
    }
    div[data-testid="stButton"] > button:active {
        transform: translateY(6px) !important; /* ปรับให้ปุ่มยุบลง 3 มิติ */
        box-shadow: 
            0 0 0 #312e81, 
            0 2px 5px rgba(0,0,0,0.3), 
            inset 0 1px 1px rgba(255,255,255,0.2) !important;
    }

    /* 🟢 ปุ่มโหลด PDF (Emerald Green 3D) */
    .btn-pdf-single div[data-testid="stDownloadButton"] > button {
        background: linear-gradient(180deg, #10b981 0%, #059669 100%) !important;
        box-shadow: 0 6px 0 #064e3b, 0 10px 20px rgba(0,0,0,0.3), inset 0 2px 2px rgba(255,255,255,0.4) !important;
        padding: 0.8rem 1.8rem !important;
        font-size: 1.1rem !important;
    }
    .btn-pdf-single div[data-testid="stDownloadButton"] > button:hover {
        transform: translateY(2px) !important;
        box-shadow: 0 4px 0 #064e3b, 0 8px 15px rgba(0,0,0,0.3), inset 0 2px 2px rgba(255,255,255,0.4) !important;
    }
    .btn-pdf-single div[data-testid="stDownloadButton"] > button:active {
        transform: translateY(6px) !important;
        box-shadow: 0 0 0 #064e3b, 0 2px 5px rgba(0,0,0,0.3) !important;
    }

    /* 🟠 ปุ่มโหลด ZIP (Amber Gold 3D) */
    .btn-zip div[data-testid="stDownloadButton"] > button {
        background: linear-gradient(180deg, #f59e0b 0%, #d97706 100%) !important;
        box-shadow: 0 6px 0 #78350f, 0 10px 20px rgba(0,0,0,0.3), inset 0 2px 2px rgba(255,255,255,0.4) !important;
        padding: 0.8rem 1.8rem !important;
        font-size: 1.1rem !important;
    }
    .btn-zip div[data-testid="stDownloadButton"] > button:hover {
        transform: translateY(2px) !important;
        box-shadow: 0 4px 0 #78350f, 0 8px 15px rgba(0,0,0,0.3), inset 0 2px 2px rgba(255,255,255,0.4) !important;
    }
    .btn-zip div[data-testid="stDownloadButton"] > button:active {
        transform: translateY(6px) !important;
        box-shadow: 0 0 0 #78350f, 0 2px 5px rgba(0,0,0,0.3) !important;
    }

    /* ✨ เอฟเฟกต์แสงวิ่งพาดปุ่ม (Shining Light) */
    div[data-testid="stButton"] > button::after,
    div[data-testid="stDownloadButton"] > button::after {
        content: '';
        position: absolute;
        top: 0; left: -100%;
        width: 50%; height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.5), transparent);
        transform: skewX(-20deg);
        animation: button-shine 4s cubic-bezier(0.4, 0, 0.2, 1) infinite;
        pointer-events: none; /* ป้องกันการบังการคลิก */
    }

    @keyframes button-shine {
        0% { left: -100%; }
        15% { left: 200%; }
        100% { left: 200%; } /* หน่วงเวลาให้แสงไม่วิ่งถี่เกินไป */
    }

    /* Premium Header Dashboard */
    .premium-header {
        position: relative;
        overflow: hidden;
        display: flex;
        align-items: center;
        gap: 20px;
        padding: 35px 40px;
        background: var(--primary-gradient);
        border-radius: 24px;
        box-shadow: var(--shadow-glow);
        margin-bottom: 30px;
        color: white;
    }

    .premium-header::before {
        content: '';
        position: absolute;
        top: -50%; left: -50%;
        width: 200%; height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 60%);
        transform: rotate(30deg);
        pointer-events: none;
    }

    .header-icon {
        font-size: 3.5rem;
        animation: floating 4s ease-in-out infinite;
        filter: drop-shadow(0 10px 15px rgba(0,0,0,0.2));
    }

    .header-text h1 {
        margin: 0;
        font-size: 2.2rem;
        font-weight: 700;
        letter-spacing: -0.5px;
        color: white;
    }

    .header-text p {
        margin: 5px 0 0 0;
        opacity: 0.85;
        font-weight: 300;
        font-size: 1.1rem;
    }

    /* Glassmorphism Cards */
    .glass-card {
        background: var(--glass-bg);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid var(--glass-border);
        border-radius: var(--border-radius);
        padding: 20px 24px;
        box-shadow: var(--shadow-soft);
        margin-bottom: 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        transition: all var(--transition-speed) ease;
    }
    
    .glass-card:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-glow);
    }

    div[data-testid="stTextInput"] input, div[data-testid="stSelectbox"] div[role="combobox"] {
        border-radius: 14px !important;
        border: 1px solid rgba(255,255,255,0.65) !important;
        background: linear-gradient(180deg, rgba(255,255,255,0.95) 0%, rgba(226,232,240,0.9) 100%) !important;
        color: var(--text-main) !important;
        padding: 10px 16px !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 5px 0 #cbd5e1, 0 9px 18px rgba(15,23,42,0.18), inset 0 2px 3px rgba(255,255,255,0.9) !important;
    }

    div[data-testid="stTextInput"] input::placeholder {
        color: #000000 !important;
        opacity: 1 !important;
    }

    /* Dropdown แบบนูน 3 มิติ */
    div[data-testid="stSelectbox"] div[role="combobox"] {
        cursor: pointer !important;
        min-height: 44px !important;
        position: relative !important;
        overflow: hidden !important;
        box-shadow: 0 6px 0 #cbd5e1, 0 12px 22px rgba(15,23,42,0.22), inset 0 2px 3px rgba(255,255,255,0.95) !important;
    }

    /* แสงสะท้อนวิ่งบนช่อง Dropdown */
    div[data-testid="stSelectbox"] div[role="combobox"]::after {
        content: '';
        position: absolute;
        top: 0;
        left: -75%;
        width: 42%;
        height: 100%;
        background: linear-gradient(105deg, transparent, rgba(255,255,255,0.7), transparent);
        transform: skewX(-20deg);
        animation: dropdown-shine 4.5s ease-in-out infinite;
        pointer-events: none;
    }

    @keyframes dropdown-shine {
        0%, 35% { left: -75%; }
        65%, 100% { left: 140%; }
    }

    div[data-testid="stSelectbox"] div[role="combobox"]:hover {
        transform: translateY(-2px) !important;
        border-color: #a78bfa !important;
        box-shadow: 0 7px 0 #a5b4fc, 0 13px 24px rgba(124,58,237,0.25), inset 0 2px 3px rgba(255,255,255,0.95) !important;
    }

    div[data-testid="stSelectbox"] div[role="combobox"]:active {
        transform: translateY(3px) !important;
        box-shadow: 0 2px 0 #a5b4fc, 0 4px 8px rgba(15,23,42,0.18), inset 0 2px 4px rgba(0,0,0,0.08) !important;
    }
    
    div[data-testid="stTextInput"] input:focus, div[data-testid="stSelectbox"] div[role="combobox"]:focus {
        border-color: #7C3AED !important;
        box-shadow: 0 5px 0 #a78bfa, 0 0 0 4px rgba(124, 58, 237, 0.2), 0 11px 22px rgba(124,58,237,0.22) !important;
    }

    /* PDF Preview Box */
    .pdf-preview-container {
        border-radius: 16px;
        overflow: hidden;
        border: 2px solid var(--glass-border);
        box-shadow: var(--shadow-soft);
        background: #1e1e1e;
    }

    /* Tabs Styling */
    div[data-testid="stTabs"] button[role="tab"] {
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        padding-bottom: 12px !important;
    }
    div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
        color: #7C3AED !important;
    }
    
    /* Badge styling */
    .status-badge {
        background: rgba(124, 58, 237, 0.1);
        color: #7C3AED;
        padding: 6px 16px;
        border-radius: 30px;
        font-weight: 700;
        font-size: 0.95rem;
        border: 1px solid rgba(124, 58, 237, 0.2);
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ==========================================
# Premium Header (Dashboard Style)
# ==========================================
st.markdown(
    """
<div class="premium-header animate-fade-in">
    <div class="header-icon">🗃️</div>
    <div class="header-text">
        <h1>Doc Finder</h1>
        <p>Intelligent Document Management & Retrieval System</p>
    </div>
</div>
""",
    unsafe_allow_html=True,
)


# ==========================================
# 3. Optimization Helpers (Session & Caching)
# ==========================================
@st.cache_resource
def get_http_session():
    session = requests.Session()
    return session


# ==========================================
# 4. Functions อ่าน Google Sheet & ดึงไฟล์ Drive
# ==========================================
@st.cache_data(ttl=300)
def load_google_sheet_data(sheet_id):
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    df = pd.read_csv(url)

    col_folder = df.columns[0]
    col_name = df.columns[1]
    col_d = df.columns[3] if len(df.columns) > 3 else df.columns[0]
    col_e = df.columns[4] if len(df.columns) > 4 else df.columns[0]
    col_f = df.columns[5] if len(df.columns) > 5 else df.columns[0]
    col_k = df.columns[10] if len(df.columns) > 10 else df.columns[0]
    col_l = df.columns[11] if len(df.columns) > 11 else df.columns[0]

    df[col_folder] = df[col_folder].astype(str).str.strip()
    df[col_name] = df[col_name].astype(str).str.strip()

    df[col_name] = df[col_name].replace(r"^\s*$", pd.NA, regex=True)
    df = df.dropna(subset=[col_name])

    cols_to_show = [
        c
        for c in [col_folder, col_name, col_d, col_e, col_f, col_k, col_l]
        if c in df.columns
    ]
    return df, col_folder, col_name, cols_to_show


@st.cache_data(ttl=600, show_spinner=False)
def get_all_files_in_folder(script_url, folder_id, subfolder_name=""):
    session = get_http_session()
    params = {
        "folder_id": folder_id,
        "subfolder": subfolder_name.strip(),
    }
    try:
        res = session.get(script_url, params=params, timeout=30)

        if res.status_code != 200:
            st.error(
                f"Google Apps Script ตอบกลับด้วยสถานะ: HTTP {res.status_code}"
            )
            return [], ""

        try:
            data = res.json()
        except ValueError:
            st.error(
                "❌ ไม่สามารถอ่านข้อมูลได้: Google Apps Script คืนค่าเป็น HTML แทนที่จะเป็น JSON"
            )
            return [], ""

        if data.get("success"):
            return data.get("files", []), data.get("searched_folder", "")
        else:
            st.warning(
                f"คำเตือนจาก Drive: {data.get('error', 'ไม่พบโฟลเดอร์')}"
            )
            return [], ""

    except requests.exceptions.Timeout:
        st.error("⏰ การเชื่อมต่อหมดเวลา (Timeout) โปรดลองใหม่อีกครั้ง")
        return [], ""
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการดึงรายการไฟล์: {e}")
        return [], ""


@st.cache_data(ttl=600, show_spinner=False)
def download_file_by_id(file_id):
    session = get_http_session()
    download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
    try:
        res = session.get(download_url, timeout=45)
        if res.status_code == 200:
            return res.content
        return None
    except Exception:
        return None


def clean_text(text):
    return re.sub(r"[^a-zA-Z0-9]", "", str(text)).lower()


def get_pdf_download_name(col_b_name):
    name_str = str(col_b_name).strip()
    if not name_str.lower().endswith(".pdf"):
        return f"{name_str}.pdf"
    return name_str


# โหลดข้อมูล Sheet
try:
    df, col_folder, col_name, cols_to_show = load_google_sheet_data(
        SPREADSHEET_ID
    )
except Exception as e:
    st.error(f"❌ เกิดข้อผิดพลาดในการโหลดข้อมูล Google Sheet: {e}")
    st.stop()

# State Management
if "search_input" not in st.session_state:
    st.session_state.search_input = ""
if "favorites" not in st.session_state:
    st.session_state.favorites = []
if "batch_selected" not in st.session_state:
    st.session_state.batch_selected = []


def clear_text():
    st.session_state.search_input = ""


def on_select_favorite():
    selected = st.session_state.get("fav_select_box")
    if selected and selected != "-- เลือกรายการโปรด --":
        st.session_state.search_input = selected


def select_all_batch(filtered_items):
    st.session_state.batch_selected = filtered_items


def clear_all_batch():
    st.session_state.batch_selected = []


# ==========================================
# Sidebar (App Navigation & Tools)
# ==========================================
with st.sidebar:
    # 🎛️ Control Panel (Glowing & Spinning Border Effect)
    st.markdown(
        """
        <div class="sidebar-glow-panel">
            <div class="panel-content">
                <span style="font-size: 1.5rem; text-shadow: none;">🎛️</span> Control Panel
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown("##### 🔍 ค้นหาเอกสาร")
    search = st.text_input(
        "",
        key="search_input",
        placeholder="พิมพ์ชื่อ Item หรือ Part...",
        label_visibility="collapsed",
    )
    st.button("🧹 ล้างการค้นหา", on_click=clear_text, use_container_width=True)

    st.markdown("<hr style='opacity: 0.2;'>", unsafe_allow_html=True)
    
    st.markdown("##### ⭐ Quick Access (รายการโปรด)")
    if st.session_state.favorites:
        st.selectbox(
            "เลือกรายการโปรด:",
            options=["-- เลือกรายการโปรด --"] + st.session_state.favorites,
            key="fav_select_box",
            on_change=on_select_favorite,
            label_visibility="collapsed"
        )
        if st.button("🗑️ ล้างรายการ", use_container_width=True):
            st.session_state.favorites = []
            st.rerun()
    else:
        st.caption("✨ กดดาวที่ชิ้นงานเพื่อบันทึกไว้ที่นี่")

    st.markdown("<hr style='opacity: 0.2;'>", unsafe_allow_html=True)
    
    st.markdown("##### ⚙️ System Settings")
    if st.button(
        "🔄 ซิงก์ข้อมูลล่าสุด", use_container_width=True
    ):
        st.cache_data.clear()
        st.toast("✅ อัปเดตฐานข้อมูลสำเร็จ!", icon="🚀")
        st.rerun()

# Filter Data
if search:
    match_folder = (
        df[col_folder].astype(str).str.contains(search, case=False, na=False)
    )
    match_name = (
        df[col_name].astype(str).str.contains(search, case=False, na=False)
    )
    filtered_df = df[match_folder | match_name]
else:
    filtered_df = df

# ==========================================
# Main Dashboard Content
# ==========================================
st.markdown(
    f"""
<div class="glass-card animate-fade-in" style="animation-delay: 0.1s;">
    <div>
        <h3 style="margin:0; display:flex; align-items:center; gap:10px;">
            <span style="font-size: 1.4rem;">📊</span> Database Overview
        </h3>
        <span style="font-size: 0.9rem; opacity: 0.7;">ระบบดึงข้อมูลแบบ Real-time จาก Spreadsheet</span>
    </div>
    <div class="status-badge">
        พบข้อมูล {len(filtered_df):,} รายการ
    </div>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown('<div class="animate-fade-in" style="animation-delay: 0.2s;">', unsafe_allow_html=True)
st.dataframe(
    filtered_df[cols_to_show], use_container_width=True, hide_index=True
)
st.markdown('</div>', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# Tabs Configuration
tab_single, tab_batch = st.tabs(
    ["📄 Document Viewer (ดูรายชิ้น)", "📦 Batch Export (ดาวน์โหลดเป็นชุด)"]
)

# --- TAB 1: Single View ---
with tab_single:
    st.markdown('<div class="animate-fade-in" style="animation-delay: 0.1s;">', unsafe_allow_html=True)
    all_item_names = filtered_df[col_name].astype(str).tolist()

    col_sel, col_star = st.columns([7, 3], vertical_alignment="bottom")
    with col_sel:
        selected_name = st.selectbox(
            "📍 เลือกรหัส/ชื่อชิ้นงานที่ต้องการดูรายละเอียด:",
            options=all_item_names,
            index=None,
            placeholder="คลิกเพื่อเลือก หรือพิมพ์ค้นหา...",
        )

    with col_star:
        if selected_name:
            is_fav = selected_name in st.session_state.favorites
            btn_label = "🌟 ลบออกจากรายการโปรด" if is_fav else "⭐ บันทึกเข้า Quick Access"
            if st.button(btn_label, use_container_width=True):
                if is_fav:
                    st.session_state.favorites.remove(selected_name)
                else:
                    st.session_state.favorites.append(selected_name)
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    if selected_name:
        selected_rows = filtered_df[
            filtered_df[col_name].astype(str).eq(selected_name)
        ]
        # ดึงชื่อโฟลเดอร์จากแถว A
        subfolder_name = (
            str(selected_rows.iloc[0][col_folder])
            if not selected_rows.empty
            else ""
        )

        with st.spinner(
            f"📡 System processing: Scanning folder `{subfolder_name or 'Root'}`..."
        ):
            files_found, folder_used = get_all_files_in_folder(
                APPS_SCRIPT_URL, FOLDER_ID, subfolder_name
            )

        if files_found:
            target_clean = clean_text(selected_name)
            matched_file = None

            for file_info in files_found:
                file_clean = clean_text(file_info["name"])
                if target_clean in file_clean or file_clean in target_clean:
                    matched_file = file_info
                    break

            if not matched_file and len(files_found) > 0:
                matched_file = files_found[0]

            if matched_file:
                pdf_bytes = download_file_by_id(matched_file["id"])
                if pdf_bytes:
                    download_filename = get_pdf_download_name(selected_name)
                    size_mb = (
                        f"{int(matched_file['size']) / (1024 * 1024):.2f} MB"
                        if matched_file.get("size")
                        else "Unknown Size"
                    )
                    
                    st.markdown(
                        f"""
                        <div class="glass-card animate-fade-in" style="margin-top: 20px; border-left: 5px solid #10B981;">
                            <div>
                                <h4 style="margin:0; color: #10B981;">✅ File Ready</h4>
                                <span style="font-size: 0.9rem;">ดึงไฟล์สำเร็จจากโฟลเดอร์ <b>{folder_used}</b> (Size: {size_mb})</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True
                    )

                    st.markdown(
                        '<div class="btn-pdf-single animate-fade-in">', unsafe_allow_html=True
                    )
                    st.download_button(
                        label=f"📥 Download Secure PDF : {download_filename}",
                        data=pdf_bytes,
                        file_name=download_filename,
                        mime="application/pdf",
                        use_container_width=True,
                    )
                    st.markdown("</div>", unsafe_allow_html=True)

                    st.markdown("<br><h4 class='animate-fade-in'>👀 Smart Preview</h4>", unsafe_allow_html=True)

                    base64_pdf = base64.b64encode(pdf_bytes).decode("utf-8")
                    pdf_display = f"""
                    <div class="pdf-preview-container animate-fade-in">
                        <object data="data:application/pdf;base64,{base64_pdf}" type="application/pdf" width="100%" height="800px">
                            <embed src="data:application/pdf;base64,{base64_pdf}" type="application/pdf" width="100%" height="800px" />
                            <div style="padding: 30px; text-align: center; color: var(--text-muted);">
                                ⚠️ เบราว์เซอร์ไม่รองรับการแสดงผล PDF โดยตรง กรุณากดปุ่มดาวน์โหลดเอกสารด้านบน
                            </div>
                        </object>
                    </div>
                    """
                    st.markdown(pdf_display, unsafe_allow_html=True)
                else:
                    st.error("❌ System Error: ไม่สามารถดาวน์โหลดไฟล์จาก Google Drive ได้")
        else:
            st.error(
                f"❌ File Not Found: ไม่มีข้อมูลในโฟลเดอร์ `{subfolder_name or 'Root'}`"
            )

# --- TAB 2: Batch Download ---
with tab_batch:
    st.markdown('<div class="animate-fade-in" style="animation-delay: 0.1s;">', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="glass-card" style="border-left: 5px solid #7C3AED; border-radius: 16px; padding: 15px 24px;">
            <h4 style="margin:0; color: #7C3AED;">📦 Batch Zip Exporter</h4>
            <span style="font-size: 0.9rem; opacity: 0.8;">เลือกรหัสชิ้นงานที่ต้องการ เพื่อมัดรวมและดาวน์โหลดเป็นไฟล์ ZIP ไฟล์เดียว</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    filtered_items = filtered_df[col_name].astype(str).tolist()

    col_b1, col_b2 = st.columns([1, 1])
    with col_b1:
        st.button(
            "✅ Select All (เลือกรายการที่ค้นพบทั้งหมด)",
            on_click=select_all_batch,
            args=(filtered_items,),
            use_container_width=True,
        )
    with col_b2:
        st.button(
            "🧹 Clear All (ล้างการเลือกทั้งหมด)",
            on_click=clear_all_batch,
            use_container_width=True,
        )

    batch_selected = st.multiselect(
        "เลือกรายการที่ต้องการส่งออก:",
        options=df[col_name].astype(str).tolist(),
        key="batch_selected",
        placeholder="คลิกเพื่อเลือกไฟล์..."
    )

    if batch_selected:
        st.markdown(f"<div style='text-align: right; margin-bottom: 15px;'><span class='status-badge'>เตรียมดาวน์โหลด <b>{len(batch_selected)}</b> รายการ</span></div>", unsafe_allow_html=True)
        
        if st.button(
            "🚀 Generate & Download ZIP Package", use_container_width=True
        ):
            zip_buffer = io.BytesIO()
            with st.spinner("🔄 Processing System: กำลังรวบรวมไฟล์และบีบอัดข้อมูล (กรุณารอสักครู่)..."):
                with zipfile.ZipFile(
                    zip_buffer, "w", zipfile.ZIP_DEFLATED
                ) as zip_file:
                    for name in batch_selected:
                        sub_rows = df[
                            df[col_name].astype(str).str.strip().eq(name.strip())
                        ]
                        subfolder_name = (
                            str(sub_rows.iloc[0][col_folder])
                            if not sub_rows.empty
                            else ""
                        )

                        files_found, _ = get_all_files_in_folder(
                            APPS_SCRIPT_URL, FOLDER_ID, subfolder_name
                        )

                        if files_found:
                            target_clean = clean_text(name)
                            matched_file = None
                            for f_info in files_found:
                                if (
                                    target_clean in clean_text(f_info["name"])
                                    or clean_text(f_info["name"])
                                    in target_clean
                                ):
                                    matched_file = f_info
                                    break

                            if not matched_file and len(files_found) > 0:
                                matched_file = files_found[0]

                            if matched_file:
                                p_bytes = download_file_by_id(
                                    matched_file["id"]
                                )
                                if p_bytes:
                                    zip_file_name = get_pdf_download_name(name)
                                    zip_file.writestr(zip_file_name, p_bytes)

                zip_buffer.seek(0)

            st.markdown('<div class="btn-zip animate-fade-in">', unsafe_allow_html=True)
            st.download_button(
                label=f"📦 บันทึกไฟล์ ZIP ลงเครื่อง ({len(batch_selected)} ไฟล์)",
                data=zip_buffer,
                file_name=f"SEEKER_Batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                mime="application/zip",
                use_container_width=True,
            )
            st.markdown("</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)