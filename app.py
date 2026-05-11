import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import os
import calendar
from dateutil.relativedelta import relativedelta
import json

# --- 1. ตั้งค่าหน้าเพจ ---
st.set_page_config(page_title="Smart To-Do Dashboard", layout="wide")

st.markdown("""
    <style>
    .metric-card { background-color: #ffffff; border: 2px solid #8064A2; border-radius: 12px; padding: 20px; margin-bottom: 20px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1); color: #333333; }
    .metric-title { color: #8064A2; font-size: 18px; font-weight: bold; margin-bottom: 10px; }
    .metric-value { color: #604A7B; font-size: 40px; font-weight: bold; line-height: 1.2; }
    .metric-subtitle { color: #888; font-size: 14px; margin-top: 5px; }
    .cal-table {width: 100%; border-collapse: collapse; table-layout: fixed; color: #333333;}
    .cal-th {background-color: #8064A2; color: white; text-align: center; padding: 10px; border: 1px solid #DDDDDD;}
    .cal-td {background-color: #FFFFFF; border: 1px solid #DDDDDD; height: 120px; vertical-align: top; padding: 5px;}
    .cal-td.other-month {background-color: #F0F0F0; color: #888;}
    .cal-td.today {background-color: #FFF2CC; border: 2px solid #F6B26B;}
    .date-num {font-weight: bold; margin-bottom: 5px; color: #8064A2;}
    .task-badge {background-color: #E4DFEC; color: #604A7B; padding: 4px 8px; border-radius: 4px; font-size: 12px; margin-bottom: 4px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; border-left: 3px solid #8064A2;}
    .task-badge.done {background-color: #C6EFCE; color: #006100; border-left: 3px solid #006100;}
    .table-header { color: #604A7B; font-size: 18px; font-weight: bold; border-left: 5px solid #8064A2; padding-left: 10px; margin-bottom: 15px; }
    .overdue-banner { background-color: #FF4B4B; color: white; padding: 15px; border-radius: 10px; margin-bottom: 25px; border-left: 10px solid #8B0000; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    
    .matrix-box { padding: 20px; border-radius: 12px; min-height: 250px; height: auto; color: #333; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 20px; }
    .matrix-q1 { background-color: #FFE5E5; border: 2px solid #FF4B4B; }
    .matrix-q2 { background-color: #E5F3FF; border: 2px solid #0068C9; }
    .matrix-q3 { background-color: #FFF2CC; border: 2px solid #F6B26B; }
    .matrix-q4 { background-color: #E8F5E9; border: 2px solid #6AA84F; }
    
    .app-credit { color: #604A7B; font-size: 16px; font-style: italic; margin-top: -15px; margin-bottom: 20px; }
    .checklist-box { background-color: #FAFAFA; border: 1px solid #E0E0E0; padding: 15px; border-radius: 8px; margin-top: 10px; }
    
    .chat-box { background-color: #F8F9FA; padding: 10px 15px; border-radius: 10px; margin-bottom: 10px; border-left: 4px solid #8064A2; }
    .chat-user { font-weight: bold; color: #8064A2; font-size: 12px; }
    .chat-time { color: #888; font-size: 11px; margin-left: 10px; }
    .chat-msg { color: #333; margin-top: 5px; font-size: 14px; }
    
    .login-container { padding: 30px; background-color: white; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); border-top: 8px solid #8064A2; margin-bottom: 20px;}
    </style>
""", unsafe_allow_html=True)

# --- 2. ระบบบัญชีผู้ใช้งาน ---
USERS_FILE = "users.json"

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as f: return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f: json.dump(users, f, ensure_ascii=False, indent=4)

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
if 'selected_user' not in st.session_state:
    st.session_state.selected_user = ""

users_db = load_users()
all_users_list = list(users_db.keys())

# ==========================================
# หน้าจอเข้าสู่ระบบ
# ==========================================
if not st.session_state.logged_in:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<h1 style="text-align: center; color: #8064A2;">🔐 Team To-Do Login</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #888;">เข้าสู่ระบบเพื่อจัดการงานส่วนตัวและงานของทีม</p><br>', unsafe_allow_html=True)
    
    col_blank1, col_login, col_quick, col_blank2 = st.columns([1, 4, 3, 1])
    
    with col_login:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        tab_login, tab_register = st.tabs(["🔑 เข้าสู่ระบบ", "📝 สมัครผู้ใช้ใหม่"])
        
        with tab_login:
            with st.form("login_form"):
                login_user = st.text_input("👤 ชื่อผู้ใช้งาน (Username)", value=st.session_state.selected_user)
                login_pass = st.text_input("🔑 รหัสผ่าน (Password)", type="password")
                submit_login = st.form_submit_button("เข้าสู่ระบบ", use_container_width=True, type="primary")
                if submit_login:
                    if login_user in users_db and users_db[login_user] == login_pass:
                        st.session_state.logged_in = True
                        st.session_state.username = login_user
                        st.rerun()
                    else: st.error("❌ ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง!")
                    
        with tab_register:
            with st.form("register_form"):
                reg_user = st.text_input("👤 ตั้งชื่อผู้ใช้งานใหม่")
                reg_pass = st.text_input("🔑 ตั้งรหัสผ่านใหม่", type="password")
                reg_pass_confirm = st.text_input("🔑 ยืนยันรหัสผ่านอีกครั้ง", type="password")
                submit_reg = st.form_submit_button("สมัครสมาชิก", use_container_width=True)
                if submit_reg:
                    if not reg_user or not reg_pass: st.warning("⚠️ กรุณากรอกข้อมูลให้ครบถ้วน")
                    elif reg_user in users_db: st.error("❌ ชื่อผู้ใช้นี้มีคนใช้งานแล้ว กรุณาใช้ชื่ออื่น")
                    elif reg_pass != reg_pass_confirm: st.error("❌ รหัสผ่านไม่ตรงกัน!")
                    else:
                        users_db[reg_user] = reg_pass
                        save_users(users_db)
                        st.success("✅ สมัครสมาชิกสำเร็จ! กรุณากลับไปที่แท็บ 'เข้าสู่ระบบ'")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_quick:
        st.markdown('<div class="login-container" style="border-top: 8px solid #F6B26B;">', unsafe_allow_html=True)
        st.markdown('<h4 style="color:#595959; margin-top:0;">⚡ เข้าสู่ระบบด่วน</h4>', unsafe_allow_html=True)
        st.write("คลิกที่ชื่อโปรไฟล์ของคุณ ระบบจะกรอกให้ทันที")
        if users_db:
            for u in users_db.keys():
                if st.button(f"👤 เข้าสู่ระบบบัญชี: {u}", use_container_width=True, key=f"quick_btn_{u}"):
                    st.session_state.selected_user = u
                    st.rerun()
        else:
            st.info("ยังไม่มีข้อมูลผู้ใช้งานในระบบครับ")
        st.markdown('</div>', unsafe_allow_html=True)

else:
    username = st.session_state.username
    CAT_FILE = "team_categories.csv"
    DATA_FILE = "team_tasks.csv"
    ARCHIVE_FILE = "team_archive_tasks.csv"
    RECYCLE_FILE = "team_recycle_bin.csv" # ♻️ ไฟล์สำหรับเก็บงานที่ถูกลบ

    def load_categories():
        if os.path.exists(CAT_FILE): return pd.read_csv(CAT_FILE)['Category'].dropna().tolist()
        else:
            defaults = ["ระบบ / ไอที", "งาน R&D", "บ้าน & DIY", "ตู้ปลา", "ทั่วไป"]
            pd.DataFrame({"Category": defaults}).to_csv(CAT_FILE, index=False)
            return defaults

    def save_categories(cat_list): pd.DataFrame({"Category": cat_list}).to_csv(CAT_FILE, index=False)

    def load_data(file_path, all_categories=None):
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            if all_categories is not None: df['Category'] = df['Category'].fillna(all_categories[0] if all_categories else "ทั่วไป").str.strip()
            if 'Priority' in df.columns: df['Priority'] = df['Priority'].fillna("ต่ำ").str.strip()
            if 'Status' in df.columns: df['Status'] = df['Status'].fillna("ยังไม่เริ่ม").str.strip()
            if 'Recurring' not in df.columns: df['Recurring'] = "ไม่ทำซ้ำ"
            if 'Notes' not in df.columns: df['Notes'] = ""
            df['Notes'] = df['Notes'].fillna("").astype(str).replace('nan', '')
            if 'Checklist' not in df.columns: df['Checklist'] = "{}"
            df['Checklist'] = df['Checklist'].fillna("{}")
            if 'Comments' not in df.columns: df['Comments'] = "[]"
            df['Comments'] = df['Comments'].fillna("[]")
            if 'Audit_Log' not in df.columns: df['Audit_Log'] = "[]"
            df['Audit_Log'] = df['Audit_Log'].fillna("[]")
            if 'Assignees' not in df.columns: df['Assignees'] = username
            df['Assignees'] = df['Assignees'].fillna(username).astype(str)
            if 'Visibility' not in df.columns: df['Visibility'] = "ทีม (Public)"
            df['Visibility'] = df['Visibility'].fillna("ทีม (Public)")
            if 'Deleted_At' not in df.columns: df['Deleted_At'] = pd.NaT # สำหรับถังขยะ
            
            for col in ['วันที่เพิ่มงาน', 'Due Date', 'เริ่มทำวันที่', 'ทำถึงวันที่', 'Deleted_At']:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
        else:
            columns = ['ลำดับ', 'วันที่เพิ่มงาน', 'Task', 'Assignees', 'Visibility', 'Category', 'Priority', 'Recurring', 'Due Date', 'เริ่มทำวันที่', 'ทำถึงวันที่', 'Status', 'Notes', 'Checklist', 'Comments', 'Audit_Log', 'Deleted_At']
            df = pd.DataFrame(columns=columns)
        return df

    def save_data(df, file_path): df.to_csv(file_path, index=False)

    def calculate_next_due_date(current_due_date, recurring_type):
        if pd.isna(current_due_date): return pd.NaT
        if recurring_type == "ทุกวัน": return current_due_date + timedelta(days=1)
        if recurring_type == "ทุกสัปดาห์": return current_due_date + timedelta(days=7)
        if recurring_type == "ทุกเดือน": return current_due_date + relativedelta(months=1)
        if recurring_type == "ทุกปี": return current_due_date + relativedelta(years=1)
        return current_due_date

    def get_cat_color(cat_name):
        colors = ["#E63946", "#2B2D42", "#F9CA24", "#2E86DE", "#8E44AD", "#FF9FF3", "#10AC84", "#FF9F43", "#5F27CD", "#1DD1A1"]
        idx = sum(ord(c) for c in str(cat_name)) % len(colors)
        return colors[idx]

    def create_log(action_text):
        return {"time": datetime.now().strftime("%d/%m %H:%M"), "action": action_text, "user": username}

    all_categories = load_categories()
    global_df = load_data(DATA_FILE, all_categories)
    global_df_archive = load_data(ARCHIVE_FILE)
    global_df_recycle = load_data(RECYCLE_FILE)

    # 🧹 ระบบ Auto-Cleanup: ลบงานในถังขยะที่อายุเกิน 30 วันอัตโนมัติ
    if not global_df_recycle.empty:
        thirty_days_ago = pd.Timestamp.now().normalize() - timedelta(days=30)
        original_len = len(global_df_recycle)
        global_df_recycle = global_df_recycle[global_df_recycle['Deleted_At'] > thirty_days_ago]
        if len(global_df_recycle) < original_len:
            save_data(global_df_recycle, RECYCLE_FILE)

    with st.sidebar:
        st.markdown(f"### 👤 ใช้งานในชื่อ: **{username}**")
        if st.button("🚪 ออกจากระบบ (Logout)", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.selected_user = "" 
            st.rerun()
        
        st.markdown("---")
        
        # ♻️ ถังขยะกู้คืนข้อมูล (Recycle Bin) บน Sidebar
        with st.popover("♻️ ถังขยะ (Recycle Bin)", use_container_width=True):
            st.markdown("##### 🗑️ รายการที่ถูกลบ (เก็บไว้ 30 วัน)")
            if global_df_recycle.empty:
                st.info("ถังขยะว่างเปล่า")
            else:
                # กรองแสดงเฉพาะงานที่ตัวเองมีสิทธิ์เห็นหรือรับผิดชอบ
                my_recycle = global_df_recycle[global_df_recycle['Assignees'].apply(lambda x: username in str(x))].copy()
                if my_recycle.empty:
                    st.info("ไม่มีรายการที่คุณลบ")
                else:
                    for idx, row in my_recycle.iterrows():
                        with st.container(border=True):
                            st.write(f"**{row['Task']}**")
                            del_time = row['Deleted_At'].strftime('%d/%m %H:%M') if pd.notna(row['Deleted_At']) else 'ไม่ระบุ'
                            st.caption(f"ลบเมื่อ: {del_time}")
                            
                            c1, c2 = st.columns(2)
                            if c1.button("🔄 กู้คืน", key=f"res_{idx}", use_container_width=True):
                                # ดึงงานกลับไปที่ฐานข้อมูลหลัก
                                row['Deleted_At'] = pd.NaT
                                global_df = pd.concat([global_df, pd.DataFrame([row])], ignore_index=True)
                                global_df_recycle = global_df_recycle.drop(idx)
                                save_data(global_df, DATA_FILE)
                                save_data(global_df_recycle, RECYCLE_FILE)
                                st.rerun()
                                
                            if c2.button("💀 ลบทิ้ง", key=f"del_{idx}", use_container_width=True):
                                # ลบถาวรออกจากระบบ
                                global_df_recycle = global_df_recycle.drop(idx)
                                save_data(global_df_recycle, RECYCLE_FILE)
                                st.rerun()

        st.markdown("---")
        with st.popover("➕ เพิ่มงานด่วน (Quick Add)", use_container_width=True):
            st.markdown("**เพิ่มโปรเจกต์ใหม่**")
            with st.form("quick_add_form_side", clear_on_submit=True):
                new_task = st.text_input("ชื่อภารกิจ / งาน")
                new_vis = st.radio("สิทธิ์การมองเห็น", ["ทีม (Public)", "🔒 ส่วนตัว (Private)"], horizontal=True)
                new_assignees = st.multiselect("👥 มอบหมายให้", all_users_list, default=[username])
                new_cat = st.selectbox("ประเภทงาน", all_categories)
                c_q1, c_q2 = st.columns(2)
                new_pri = c_q1.selectbox("ความสำคัญ", ["สูง", "ปานกลาง", "ต่ำ"], index=2)
                new_due = c_q2.date_input("Deadline", format="DD/MM/YYYY")
                new_rec = st.selectbox("รอบทำซ้ำ", ["ไม่ทำซ้ำ", "ทุกวัน", "ทุกสัปดาห์", "ทุกเดือน", "ทุกปี"])
                new_stat = st.selectbox("สถานะ", ["ยังไม่เริ่ม", "กำลังวางแผน", "ลงมือทำ", "ติดตามผล", "เสร็จเรียบร้อย"], index=0)
                new_notes = st.text_input("รายละเอียด/ลิงก์")
                
                if st.form_submit_button("💾 บันทึกงาน", type="primary", use_container_width=True):
                    if new_task and new_assignees:
                        finish_date = pd.Timestamp.now().replace(second=0, microsecond=0) if new_stat == "เสร็จเรียบร้อย" else pd.NaT
                        assignees_str = ", ".join(new_assignees)
                        initial_log = json.dumps([create_log("สร้างโปรเจกต์ใหม่ (ด่วน)")], ensure_ascii=False)
                        new_row = pd.DataFrame([{
                            "วันที่เพิ่มงาน": pd.Timestamp.now().replace(second=0, microsecond=0), 
                            "Task": new_task, "Assignees": assignees_str, "Visibility": new_vis, "Category": new_cat, "Priority": new_pri, "Recurring": new_rec,
                            "Due Date": pd.to_datetime(new_due), 
                            "เริ่มทำวันที่": pd.NaT, "ทำถึงวันที่": finish_date, "Status": new_stat, "Notes": new_notes, "Checklist": "{}", "Comments": "[]", "Audit_Log": initial_log, "Deleted_At": pd.NaT
                        }])
                        global_df = pd.concat([global_df, new_row], ignore_index=True)
                        save_data(global_df, DATA_FILE)
                        st.rerun()
                    else:
                        st.error("⚠️ กรุณากรอกชื่อภารกิจและผู้รับผิดชอบ")

        st.markdown("---")
        st.header("🔍 ตัวกรองอัจฉริยะ")
        filter_cat = st.selectbox("เลือกดูเฉพาะหมวดหมู่:", ["ทั้งหมด"] + all_categories)

        st.markdown("---")
        st.header("⚙️ ตั้งค่าหมวดหมู่ทีม")
        new_cat_input = st.text_input("เพิ่มประเภทงานใหม่")
        if st.button("➕ เพิ่มหมวดหมู่"):
            if new_cat_input and new_cat_input not in all_categories:
                all_categories.append(new_cat_input)
                save_categories(all_categories)
                st.rerun()
        
        with st.expander("ลบหมวดหมู่"):
            for i, cat in enumerate(all_categories):
                c1, c2 = st.columns([3, 1])
                c1.write(cat)
                if c2.button("🗑️", key=f"del_cat_{i}"):
                    all_categories.remove(cat)
                    save_categories(all_categories)
                    st.rerun()
                
        st.markdown("---")
        st.header("📦 ระบบคลังข้อมูลทีม")
        def is_assigned(assignees_str, target_user):
            if pd.isna(assignees_str): return False
            return target_user in [u.strip() for u in str(assignees_str).split(",")]
            
        if st.button("📦 ย้ายงานที่เสร็จลงกรุ (Archive)"):
            user_tasks_mask = global_df['Assignees'].apply(lambda x: is_assigned(x, username))
            completed_mask = (global_df['Status'] == "เสร็จเรียบร้อย") & user_tasks_mask
            completed_work = global_df[completed_mask].copy()
            
            if not completed_work.empty:
                global_df_archive = pd.concat([global_df_archive, completed_work], ignore_index=True)
                global_df = global_df.drop(completed_work.index) 
                
                recurring_tasks = completed_work[completed_work['Recurring'] != "ไม่ทำซ้ำ"]
                for _, row in recurring_tasks.iterrows():
                    next_due = calculate_next_due_date(row['Due Date'], row['Recurring'])
                    initial_log = json.dumps([create_log("สร้างโปรเจกต์ทำซ้ำอัตโนมัติ")], ensure_ascii=False)
                    new_task = pd.DataFrame([{
                        "วันที่เพิ่มงาน": pd.Timestamp.now().replace(second=0, microsecond=0),
                        "Task": row['Task'], "Assignees": row['Assignees'], "Visibility": row['Visibility'], "Category": row['Category'], "Priority": row['Priority'],
                        "Recurring": row['Recurring'], "Due Date": next_due,
                        "เริ่มทำวันที่": pd.NaT, "ทำถึงวันที่": pd.NaT, "Status": "ยังไม่เริ่ม", 
                        "Notes": row.get('Notes', ""), "Checklist": "{}", "Comments": "[]", "Audit_Log": initial_log, "Deleted_At": pd.NaT
                    }])
                    global_df = pd.concat([global_df, new_task], ignore_index=True)
                    
                save_data(global_df_archive, ARCHIVE_FILE)
                save_data(global_df, DATA_FILE)
                st.success(f"ย้ายงาน {len(completed_work)} รายการลงกรุเรียบร้อย!")
                st.balloons()
            else: st.warning("ไม่มีงานสถานะ 'เสร็จเรียบร้อย' ของคุณให้ย้ายครับ")

        st.markdown("---")
        csv_data = global_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(label="📥 ดาวน์โหลดข้อมูลทีม", data=csv_data, file_name=f"team_tasks_backup.csv", mime="text/csv")

    col_title, col_ver = st.columns([8, 2])
    with col_title: st.title("🎯 Team Collaboration Dashboard")
    
    with col_ver: 
        with st.popover("🚀 Version 5.3.1 (ล่าสุด)", use_container_width=True):
            st.markdown("### 📝 Changelog")
            st.markdown('''
            * **v5.3.1**: เพิ่มระบบ Recycle Bin บน Sidebar และล้างข้อมูลอัตโนมัติใน 30 วัน
            * **v5.3.0**: เพิ่มหลอด Progress Bar สีเขียว และปุ่ม '📑 Clone' สำหรับคัดลอกงานด่วนใน Kanban
            * **v5.2.0**: เพิ่มระบบสิทธิ์การมองเห็น (Public/Private) และ Audit Log ประวัติกิจกรรม
            * **v5.1.0**: เพิ่มระบบรายงานสรุปอัตโนมัติ (Automated Report) และเรดาร์วิเคราะห์ภาระงาน
            * **v5.0.0**: นำฟอร์มเพิ่มงานหลักกลับมาหน้าแรก, มี Quick Add และซ่อนวินาที
            ''')
    st.markdown('<div class="app-credit">Created by Thanayut</div>', unsafe_allow_html=True)
    st.markdown("---")

    def get_checklist_progress(json_str):
        try:
            tasks = json.loads(json_str)
            if not tasks: return ""
            done = sum(1 for v in tasks.values() if v)
            return f"({done}/{len(tasks)})"
        except: return ""

    today_ts = pd.Timestamp.now().normalize()
    if 'Due Date' in global_df.columns: global_df['Due Date'] = pd.to_datetime(global_df['Due Date'], errors='coerce')
    else: global_df['Due Date'] = pd.Series(dtype='datetime64[ns]')

    if not global_df.empty:
        global_df['Days Left'] = (global_df['Due Date'] - today_ts).dt.days
        global_df['Sub-tasks'] = global_df['Checklist'].apply(get_checklist_progress)
        
        user_mask = global_df['Assignees'].apply(lambda x: is_assigned(x, username))
        df = global_df[user_mask].copy()
        
        if filter_cat != "ทั้งหมด":
            df = df[df['Category'] == filter_cat]
            
        df['ลำดับ'] = range(1, len(df) + 1)
    else:
        df = pd.DataFrame(columns=['ลำดับ', 'วันที่เพิ่มงาน', 'Task', 'Assignees', 'Visibility', 'Sub-tasks', 'Category', 'Priority', 'Recurring', 'Due Date', 'Days Left', 'เริ่มทำวันที่', 'ทำถึงวันที่', 'Status', 'Notes', 'Checklist', 'Comments', 'Audit_Log', 'Deleted_At'])
        global_df['Days Left'] = pd.Series(dtype=float)
        global_df['Sub-tasks'] = pd.Series(dtype=str)

    column_order = ['ลำดับ', 'วันที่เพิ่มงาน', 'Task', 'Visibility', 'Assignees', 'Sub-tasks', 'Category', 'Priority', 'Recurring', 'Due Date', 'Days Left', 'เริ่มทำวันที่', 'ทำถึงวันที่', 'Status', 'Notes', 'Checklist', 'Comments', 'Audit_Log', 'Deleted_At']
    for col in column_order:
        if col not in df.columns: df[col] = None
    df = df[column_order]

    def apply_custom_styling(df_to_style):
        def style_priority(val):
            v = str(val).strip()
            if v == 'สูง': return 'background-color: #FFC7CE; color: #9C0006;'
            if v == 'ปานกลาง': return 'background-color: #FFEB9C; color: #9C6500;'
            if v == 'ต่ำ': return 'background-color: #C6EFCE; color: #006100;'
            return ''
        def style_days(val):
            if pd.isna(val): return ''
            if val < 0: return 'background-color: #FF4B4B; color: white; font-weight: bold;' 
            if val <= 1: return 'background-color: #FFC7CE; color: #9C0006;'
            if 2 <= val <= 3: return 'background-color: #FFEB9C; color: #9C6500;'
            if val > 3: return 'background-color: #C6EFCE; color: #006100;'
            return ''
        return df_to_style.style.map(style_priority, subset=['Priority']).map(style_days, subset=['Days Left'])

    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["📊 Dashboard & Tasks", "📅 Calendar View", "🗃️ Team Archive", "🗂️ Interactive Kanban", "🧠 Eisenhower Matrix", "📊 Gantt Chart", "📈 Analytics & Reports"])

    with tab1:
        total_tasks = len(df)
        completed_tasks = len(df[df['Status'] == "เสร็จเรียบร้อย"]) if total_tasks > 0 else 0
        pending_tasks = total_tasks - completed_tasks
        near_deadline_count = len(df[(df['Status'] != "เสร็จเรียบร้อย") & (df['Days Left'] <= 3) & (df['Days Left'] >= 0)]) if total_tasks > 0 else 0

        l_col, r_col = st.columns([2, 1])
        with l_col:
            c1, c2 = st.columns(2)
            c1.markdown(f'<div class="metric-card"><div class="metric-title">📝 งานของฉัน</div><div class="metric-value">{total_tasks}</div><div class="metric-subtitle">งานปัจจุบัน</div></div>', unsafe_allow_html=True)
            c2.markdown(f'<div class="metric-card"><div class="metric-title">✅ เสร็จแล้ว</div><div class="metric-value">{completed_tasks}</div><div class="metric-subtitle">รอ Archive</div></div>', unsafe_allow_html=True)
            c3, c4 = st.columns(2)
            c3.markdown(f'<div class="metric-card"><div class="metric-title">⚠️ งานค้าง</div><div class="metric-value">{pending_tasks}</div><div class="metric-subtitle">กำลังทำ</div></div>', unsafe_allow_html=True)
            c4.markdown(f'<div class="metric-card"><div class="metric-title">⏰ ใกล้ Deadline</div><div class="metric-value">{near_deadline_count}</div><div class="metric-subtitle">ภายใน 3 วัน</div></div>', unsafe_allow_html=True)
            
            if total_tasks > 0:
                progress_pct = int((completed_tasks / total_tasks) * 100)
                st.markdown(f"**เป้าหมายการเคลียร์งานวันนี้:** {progress_pct}%")
                st.progress(progress_pct / 100)

        with r_col:
            st.markdown('<div style="text-align: center; color: #8064A2; font-size: 20px; font-weight: bold; margin-bottom: 10px;">ความคืบหน้ารวม</div>', unsafe_allow_html=True)
            if total_tasks > 0:
                pct = int((completed_tasks/total_tasks)*100)
                fig = px.pie(values=[completed_tasks, pending_tasks], names=["เสร็จแล้ว", "ยังไม่เสร็จ"], hole=0.6, color_discrete_sequence=["#8064A2", "#D9D9D9"])
                fig.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=260, showlegend=False, paper_bgcolor="rgba(0,0,0,0)", annotations=[dict(text=f"{pct}%", x=0.5, y=0.5, font_size=40, showarrow=False, font_color="#604A7B")])
                st.plotly_chart(fig, use_container_width=True)
            else: st.info("ไม่มีข้อมูล")

        st.markdown("---")

        with st.container(border=True):
            st.markdown('<div class="table-header">🚨 งานที่ต้องทำวันนี้ (เร่งด่วน / ถึงกำหนด)</div>', unsafe_allow_html=True)
            overdue_tasks = df[(df['Days Left'] < 0) & (df['Status'] != "เสร็จเรียบร้อย")]
            if not overdue_tasks.empty:
                st.markdown(f"""<div class="overdue-banner"><h3 style="color: white; margin-bottom: 5px;">🚨 แจ้งเตือน: มีงานเลยกำหนด {len(overdue_tasks)} รายการ!</h3>
                <span style="color: white;">กรุณาตรวจสอบและอัปเดตสถานะงานด่วนในตารางด้านล่าง</span></div>""", unsafe_allow_html=True)
            
            today_tasks_df = df[(df['Days Left'] <= 1) & (df['Status'] != "เสร็จเรียบร้อย")].drop(columns=['Checklist', 'Comments', 'Audit_Log', 'Deleted_At'], errors='ignore') 
            if not today_tasks_df.empty:
                st.dataframe(apply_custom_styling(today_tasks_df), use_container_width=True, hide_index=True, column_config={
                    "Due Date": st.column_config.DateColumn("วันที่ Deadline", format="DD/MM/YYYY"), 
                    "Task": st.column_config.TextColumn("ภารกิจ / งาน", width="large"), 
                    "Assignees": st.column_config.TextColumn("ผู้รับผิดชอบ"),
                    "Visibility": st.column_config.TextColumn("สิทธิ์มองเห็น"),
                    "Notes": st.column_config.LinkColumn("รายละเอียด/ลิงก์")
                })
            else: st.success("✅ เยี่ยมมาก! วันนี้ไม่มีงานค้างที่ต้องเร่งรีบ")

        st.markdown("<br>", unsafe_allow_html=True)

        with st.expander("➕ เพิ่ม/มอบหมายงานใหม่ (Assign Task)"):
            with st.form("add_task_form_main", clear_on_submit=True):
                c1, c2, c3 = st.columns([2, 1, 1])
                new_task = c1.text_input("ชื่อภารกิจ / งาน")
                new_vis = st.radio("สิทธิ์การมองเห็น", ["ทีม (Public)", "🔒 ส่วนตัว (Private)"], horizontal=True)
                new_assignees = c2.multiselect("👥 มอบหมายให้ (ใช้งานร่วมกันได้)", all_users_list, default=[username])
                new_cat = c3.selectbox("ประเภทงาน", all_categories)
                
                c4, c5, c6 = st.columns(3)
                new_pri = c4.selectbox("ความสำคัญ", ["สูง", "ปานกลาง", "ต่ำ"], index=2)
                new_rec = c5.selectbox("รอบทำซ้ำ", ["ไม่ทำซ้ำ", "ทุกวัน", "ทุกสัปดาห์", "ทุกเดือน", "ทุกปี"])
                new_due = c6.date_input("วันที่ Deadline", format="DD/MM/YYYY")
                
                c7, c8 = st.columns([1, 2])
                new_stat = c7.selectbox("สถานะ", ["ยังไม่เริ่ม", "กำลังวางแผน", "ลงมือทำ", "ติดตามผล", "เสร็จเรียบร้อย"], index=0)
                new_notes = c8.text_input("รายละเอียดเพิ่มเติม หรือใส่ URL ลิงก์", placeholder="เช่น https://www.google.com")
                
                c_btn1, c_btn2, _ = st.columns([2, 2, 8])
                submitted = c_btn1.form_submit_button("💾 บันทึกงาน", type="primary", use_container_width=True)
                cleared = c_btn2.form_submit_button("🧹 ล้างข้อมูล", use_container_width=True)
                
                if submitted:
                    if new_task and new_assignees:
                        finish_date = pd.Timestamp.now().replace(second=0, microsecond=0) if new_stat == "เสร็จเรียบร้อย" else pd.NaT
                        assignees_str = ", ".join(new_assignees)
                        initial_log = json.dumps([create_log("สร้างโปรเจกต์ใหม่")], ensure_ascii=False)
                        new_row = pd.DataFrame([{
                            "วันที่เพิ่มงาน": pd.Timestamp.now().replace(second=0, microsecond=0), 
                            "Task": new_task, "Assignees": assignees_str, "Visibility": new_vis, "Category": new_cat, "Priority": new_pri, "Recurring": new_rec,
                            "Due Date": pd.to_datetime(new_due), 
                            "เริ่มทำวันที่": pd.NaT, "ทำถึงวันที่": finish_date, "Status": new_stat, "Notes": new_notes, "Checklist": "{}", "Comments": "[]", "Audit_Log": initial_log, "Deleted_At": pd.NaT
                        }])
                        global_df = pd.concat([global_df, new_row], ignore_index=True)
                        save_data(global_df, DATA_FILE)
                        st.rerun()
                    else:
                        st.error("⚠️ กรุณากรอกชื่อภารกิจ และเลือกผู้รับผิดชอบอย่างน้อย 1 คน")

        st.markdown("<br>", unsafe_allow_html=True)

        with st.container(border=True):
            c_title, c_search = st.columns([1, 1])
            c_title.markdown('<div class="table-header">📋 รายการงานทั้งหมดของฉัน</div>', unsafe_allow_html=True)
            search_query = c_search.text_input("🔍 ค้นหางาน / หมวดหมู่", placeholder="พิมพ์คำที่ต้องการค้นหา...")

            display_df = df.copy()
            if search_query: display_df = display_df[display_df.apply(lambda row: row.astype(str).str.contains(search_query, case=False).any(), axis=1)]

            # ระบบลบลงถังขยะ (Soft Delete) โดยจับจากความยาวของตาราง
            edit_cols = display_df.drop(columns=['Checklist', 'Comments', 'Audit_Log', 'Deleted_At'], errors='ignore')
            edited_df = st.data_editor(
                apply_custom_styling(edit_cols), 
                use_container_width=True, hide_index=True, num_rows="dynamic",
                disabled=["ลำดับ", "วันที่เพิ่มงาน", "Days Left", "Sub-tasks", "Assignees"],
                column_config={
                    "วันที่เพิ่มงาน": st.column_config.DatetimeColumn("วันที่เพิ่มงาน", format="DD/MM/YYYY HH:mm"),
                    "Task": st.column_config.TextColumn("ภารกิจ / งาน", width="large", required=True),
                    "Visibility": st.column_config.SelectboxColumn("สิทธิ์", options=["ทีม (Public)", "🔒 ส่วนตัว (Private)"]),
                    "Assignees": st.column_config.TextColumn("ผู้รับผิดชอบ"),
                    "Sub-tasks": st.column_config.TextColumn("ความคืบหน้าย่อย"),
                    "Notes": st.column_config.LinkColumn("ลิงก์อ้างอิง"),
                    "Category": st.column_config.SelectboxColumn("ประเภท", options=all_categories),
                    "Priority": st.column_config.SelectboxColumn("ความสำคัญ", options=["สูง", "ปานกลาง", "ต่ำ"]),
                    "Recurring": st.column_config.SelectboxColumn("ทำซ้ำ", options=["ไม่ทำซ้ำ", "ทุกวัน", "ทุกสัปดาห์", "ทุกเดือน", "ทุกปี"]),
                    "Due Date": st.column_config.DateColumn("Deadline", format="DD/MM/YYYY"),
                    "Status": st.column_config.SelectboxColumn("สถานะ", options=["ยังไม่เริ่ม", "กำลังวางแผน", "ลงมือทำ", "ติดตามผล", "เสร็จเรียบร้อย"]),
                    "เริ่มทำวันที่": st.column_config.DateColumn("เริ่มทำวันที่", format="DD/MM/YYYY"),
                    "ทำถึงวันที่": st.column_config.DateColumn("ทำถึงวันที่", format="DD/MM/YYYY"),
                }
            )
            
            # ตรวจสอบว่ามีการลบแถวเกิดขึ้นหรือไม่
            if len(edited_df) < len(edit_cols):
                deleted_indices = set(edit_cols.index) - set(edited_df.index)
                for d_idx in deleted_indices:
                    # ย้ายงานไปพักที่ตารางถังขยะ พร้อมบันทึกเวลา
                    task_to_bin = global_df.loc[d_idx].copy()
                    task_to_bin['Deleted_At'] = pd.Timestamp.now().replace(second=0, microsecond=0)
                    global_df_recycle = pd.concat([global_df_recycle, pd.DataFrame([task_to_bin])], ignore_index=True)
                    # ลบออกจากตารางหลัก
                    global_df = global_df.drop(d_idx)
                
                save_data(global_df, DATA_FILE)
                save_data(global_df_recycle, RECYCLE_FILE)
                st.success("♻️ ย้ายรายการไปที่ถังขยะเรียบร้อยแล้ว (สามารถกู้คืนได้ที่แถบซ้ายมือ)")
                st.rerun()

            elif not edit_cols.equals(edited_df):
                final_df = edited_df.copy()
                if 'Checklist' in display_df.columns: final_df['Checklist'] = display_df['Checklist']
                else: final_df['Checklist'] = "{}"
                if 'Comments' in display_df.columns: final_df['Comments'] = display_df['Comments']
                else: final_df['Comments'] = "[]"
                if 'Audit_Log' in display_df.columns: final_df['Audit_Log'] = display_df['Audit_Log']
                else: final_df['Audit_Log'] = "[]"
                if 'Deleted_At' in display_df.columns: final_df['Deleted_At'] = display_df['Deleted_At']
                else: final_df['Deleted_At'] = pd.NaT
                
                for i in edited_df.index:
                    if not edit_cols.loc[i].equals(edited_df.loc[i]):
                        if edited_df.loc[i, 'Status'] == 'เสร็จเรียบร้อย' and pd.isna(edited_df.loc[i, 'ทำถึงวันที่']):
                            final_df.loc[i, 'ทำถึงวันที่'] = pd.Timestamp.now().replace(second=0, microsecond=0)
                        elif edited_df.loc[i, 'Status'] != 'เสร็จเรียบร้อย':
                            final_df.loc[i, 'ทำถึงวันที่'] = pd.NaT 
                        
                        logs = json.loads(final_df.loc[i, 'Audit_Log']) if pd.notna(final_df.loc[i, 'Audit_Log']) else []
                        logs.append(create_log("แก้ไขรายละเอียดงานผ่านตาราง"))
                        final_df.loc[i, 'Audit_Log'] = json.dumps(logs, ensure_ascii=False)
                
                global_df.update(final_df)
                save_data(global_df, DATA_FILE)
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        
        def ai_generate_subtasks(task_name):
            task_name = task_name.lower()
            if "เลี้ยง" in task_name or "party" in task_name:
                return {"กำหนดวันและเวลาจัดงาน": False, "จองสถานที่ / เตรียมสถานที่": False, "สั่งอาหารและเครื่องดื่ม": False, "ทำลิสต์เชิญแขก": False, "เตรียมกิจกรรม / ของขวัญ": False}
            elif "ล้างรถ" in task_name or "car" in task_name:
                return {"ฉีดน้ำล้างคราบฝุ่นรอบคัน": False, "ผสมน้ำยาล้างรถและขัดถู": False, "ล้างล้อและซุ้มล้อ": False, "ฉีดน้ำล้างฟองออกให้หมด": False, "เช็ดแห้งและดูดฝุ่นภายใน": False}
            elif "ประชุม" in task_name or "meeting" in task_name:
                return {"จองห้องประชุม / สร้างลิงก์ออนไลน์": False, "กำหนดวาระการประชุม (Agenda)": False, "ส่งอีเมลเชิญผู้เข้าร่วม": False, "เตรียมสไลด์ / เอกสาร": False, "เขียนรายงานสรุป (Minutes)": False}
            elif "เที่ยว" in task_name or "travel" in task_name:
                return {"จองตั๋วเครื่องบิน / รถเดินทาง": False, "จองโรงแรมที่พัก": False, "วางแผนจุดเช็คอินแต่ละวัน": False, "จัดกระเป๋าเดินทาง": False, "เตรียมเงิน / บัตรเครดิต": False}
            elif "คอม" in task_name or "pc" in task_name:
                return {"สำรองข้อมูลสำคัญ (Backup)": False, "เป่าฝุ่น / ทำความสะอาดเคส": False, "อัปเดต Windows & Drivers": False, "สแกนไวรัส": False}
            elif "ปลา" in task_name or "fish" in task_name:
                return {"ถ่ายน้ำเก่าออก 30%": False, "ขัดกระจก / ขัดตะไคร่": False, "ล้างใยแก้วกรองน้ำ": False, "เติมน้ำใหม่ (พักน้ำแล้ว)": False, "ใส่แบคทีเรียปรับสภาพน้ำ": False}
            else:
                return {"วางแผนขั้นตอนการทำงาน": False, "เตรียมอุปกรณ์/เครื่องมือ": False, "ลงมือปฏิบัติงาน": False, "ตรวจสอบความเรียบร้อย": False}

        if not df.empty:
            st.markdown('<div class="table-header">✅ แผงควบคุมโปรเจกต์ (Sub-tasks & Comments)</div>', unsafe_allow_html=True)
            selected_task_name = st.selectbox("📌 เลือกโปรเจกต์ที่ต้องการจัดการรายละเอียด:", df['Task'].tolist())
            
            if selected_task_name:
                task_idx = df[df['Task'] == selected_task_name].index[0]
                current_checklist = json.loads(df.loc[task_idx, 'Checklist']) if pd.notna(df.loc[task_idx, 'Checklist']) else {}
                current_comments = json.loads(df.loc[task_idx, 'Comments']) if pd.notna(df.loc[task_idx, 'Comments']) and str(df.loc[task_idx, 'Comments']).strip() != '' else []
                current_logs = json.loads(df.loc[task_idx, 'Audit_Log']) if pd.notna(df.loc[task_idx, 'Audit_Log']) and str(df.loc[task_idx, 'Audit_Log']).strip() != '' else []
                
                col_sub, col_chat = st.columns([3, 2])
                
                with col_sub:
                    st.markdown('<div class="checklist-box">', unsafe_allow_html=True)
                    
                    col_ai1, col_ai2 = st.columns([8, 4])
                    col_ai1.write(f"**📑 รายการย่อย:**")
                    if col_ai2.button("✨ ให้ AI ช่วยคิดเช็คลิสต์"):
                        ai_tasks = ai_generate_subtasks(selected_task_name)
                        current_checklist.update(ai_tasks)
                        global_df.loc[task_idx, 'Checklist'] = json.dumps(current_checklist)
                        current_logs.append(create_log("ใช้ AI สร้างรายการย่อย"))
                        global_df.loc[task_idx, 'Audit_Log'] = json.dumps(current_logs, ensure_ascii=False)
                        save_data(global_df, DATA_FILE)
                        st.rerun()
                    
                    updated_checklist = current_checklist.copy()
                    item_to_delete = None
                    
                    if not current_checklist: st.info("ยังไม่มีรายการย่อย")
                    
                    for item, is_done in current_checklist.items():
                        col1, col2 = st.columns([11, 1])
                        updated_checklist[item] = col1.checkbox(item, value=is_done, key=f"chk_{task_idx}_{item}")
                        if col2.button("❌", key=f"del_{task_idx}_{item}"):
                            item_to_delete = item
                            
                    if item_to_delete:
                        del updated_checklist[item_to_delete]
                    
                    c_new1, c_new2 = st.columns([4, 1])
                    new_sub_task = c_new1.text_input("เพิ่มงานย่อยใหม่...", key=f"new_sub_{task_idx}")
                    if c_new2.button("➕ เพิ่ม", key=f"add_sub_{task_idx}") and new_sub_task:
                        updated_checklist[new_sub_task] = False
                    
                    if json.dumps(current_checklist) != json.dumps(updated_checklist) or item_to_delete:
                        global_df.loc[task_idx, 'Checklist'] = json.dumps(updated_checklist)
                        current_logs.append(create_log("อัปเดตรายการย่อย (Sub-tasks)"))
                        global_df.loc[task_idx, 'Audit_Log'] = json.dumps(current_logs, ensure_ascii=False)
                        save_data(global_df, DATA_FILE)
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col_chat:
                    st.markdown('<div class="checklist-box">', unsafe_allow_html=True)
                    st.write("**💬 พูดคุย / อัปเดตงาน:**")
                    
                    chat_container = st.container(height=280)
                    with chat_container:
                        if not current_comments:
                            st.write("<p style='color:#888; font-size:14px; text-align:center;'><br><br>ยังไม่มีข้อความอัปเดต...</p>", unsafe_allow_html=True)
                        else:
                            msg_to_delete = None
                            for idx_msg, msg in enumerate(current_comments):
                                if msg['user'] == username:
                                    c_msg, c_del = st.columns([10, 2])
                                    with c_msg:
                                        st.markdown(f"""
                                            <div class="chat-box">
                                                <span class="chat-user">{msg['user']}</span> 
                                                <span class="chat-time">{msg['time']}</span>
                                                <div class="chat-msg">{msg['text']}</div>
                                            </div>
                                        """, unsafe_allow_html=True)
                                    with c_del:
                                        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
                                        if st.button("🗑️", key=f"del_msg_{task_idx}_{idx_msg}", help="ลบข้อความนี้"):
                                            msg_to_delete = idx_msg
                                else:
                                    st.markdown(f"""
                                        <div class="chat-box" style="background-color: #f1f1f1; border-left: 4px solid #bbb;">
                                            <span class="chat-user" style="color: #666;">{msg['user']}</span> 
                                            <span class="chat-time">{msg['time']}</span>
                                            <div class="chat-msg">{msg['text']}</div>
                                        </div>
                                    """, unsafe_allow_html=True)
                            
                            if msg_to_delete is not None:
                                current_comments.pop(msg_to_delete)
                                global_df.loc[task_idx, 'Comments'] = json.dumps(current_comments, ensure_ascii=False)
                                save_data(global_df, DATA_FILE)
                                st.rerun()
                    
                    with st.form(key=f"chat_form_{task_idx}", clear_on_submit=True):
                        c_chat1, c_chat2 = st.columns([4, 1])
                        new_comment = c_chat1.text_input("พิมพ์ข้อความ...", label_visibility="collapsed")
                        if c_chat2.form_submit_button("ส่ง ✉️", use_container_width=True) and new_comment:
                            time_now = datetime.now().strftime("%d %b %H:%M")
                            new_entry = {"user": username, "time": time_now, "text": new_comment}
                            current_comments.append(new_entry)
                            global_df.loc[task_idx, 'Comments'] = json.dumps(current_comments, ensure_ascii=False)
                            save_data(global_df, DATA_FILE)
                            st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                with st.expander("📜 ประวัติกิจกรรมการแก้ข้อมูล (Audit Log)"):
                    if not current_logs:
                        st.info("ยังไม่มีประวัติการทำกิจกรรม")
                    else:
                        for log in reversed(current_logs):
                            st.markdown(f"<span style='color: #8064A2; font-weight: bold;'>{log['user']}</span> : {log['action']} <span style='color: #888; font-size: 12px;'>({log['time']})</span>", unsafe_allow_html=True)

    with tab2:
        st.subheader("📅 ปฏิทินงานของฉันและงานทีม")
        thai_months = ["มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน", "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"]
        col_m, col_y, _ = st.columns([1, 1, 3])
        sel_m = thai_months.index(col_m.selectbox("เลือกเดือน", thai_months, index=datetime.now().month - 1)) + 1
        sel_y = col_y.selectbox("เลือกปี (ค.ศ.)", range(datetime.now().year - 1, datetime.now().year + 3), index=1)
        
        cal_obj = calendar.Calendar(firstweekday=0) 
        month_days = cal_obj.monthdatescalendar(sel_y, sel_m)
        html_cal = '<table class="cal-table"><tr>'
        for d in ["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์", "อาทิตย์"]: html_cal += f"<th class='cal-th'>{d}</th>"
        html_cal += "</tr>"
        for week in month_days:
            html_cal += "<tr>"
            for d in week:
                css = "cal-td" + (" other-month" if d.month != sel_m else "") + (" today" if d == datetime.now().date() else "")
                html_cal += f"<td class='{css}'><div class='date-num'>{d.day}</div>"
                if not df.empty:
                    day_tasks = df[df['Due Date'].dt.date == d]
                    for _, row in day_tasks.iterrows():
                        vis_icon = "🔒 " if "ส่วนตัว" in str(row.get('Visibility', '')) else ""
                        badge = "task-badge done" if row['Status'] == "เสร็จเรียบร้อย" else "task-badge"
                        html_cal += f"<div class='{badge}' title='{row['Task']}'>{vis_icon}• {row['Task']}</div>"
                html_cal += "</td>"
            html_cal += "</tr>"
        st.markdown(html_cal + "</table>", unsafe_allow_html=True)

    with tab3:
        st.markdown('<div class="table-header">📦 คลังเก็บประวัติงานทีม (Team Archive)</div>', unsafe_allow_html=True)
        if not global_df_archive.empty:
            my_archive_mask = global_df_archive['Assignees'].apply(lambda x: is_assigned(x, username))
            my_archive_df = global_df_archive[my_archive_mask]
            
            edited_archive = st.data_editor(
                my_archive_df.drop(columns=['Comments', 'Audit_Log', 'Deleted_At'], errors='ignore').style.set_properties(**{'background-color': '#f9f9f9', 'color': '#333'}), 
                use_container_width=True, hide_index=True, num_rows="dynamic",
                column_config={
                    "Checklist": None,
                    "วันที่เพิ่มงาน": st.column_config.DatetimeColumn(format="DD/MM/YYYY HH:mm")
                } 
            )
            if not my_archive_df.drop(columns=['Comments', 'Audit_Log', 'Deleted_At'], errors='ignore').equals(edited_archive):
                final_archive = edited_archive.copy()
                if 'Comments' in my_archive_df.columns: final_archive['Comments'] = my_archive_df['Comments']
                if 'Audit_Log' in my_archive_df.columns: final_archive['Audit_Log'] = my_archive_df['Audit_Log']
                if 'Deleted_At' in my_archive_df.columns: final_archive['Deleted_At'] = my_archive_df['Deleted_At']
                
                global_df_archive.update(final_archive)
                deleted_indices = set(my_archive_df.index) - set(edited_archive.index)
                global_df_archive = global_df_archive.drop(index=list(deleted_indices))
                save_data(global_df_archive, ARCHIVE_FILE)
                st.rerun()
                
            csv_archive = global_df_archive.to_csv(index=False).encode('utf-8-sig')
            st.download_button(label="📥 ดาวน์โหลดประวัติทีมทั้งหมด (CSV)", data=csv_archive, file_name=f"team_archived_history.csv", mime="text/csv")
        else:
            st.info("ยังไม่มีข้อมูลในคลังประวัติทีมครับ")

    with tab4:
        st.markdown('<div class="table-header">🗂️ Interactive Kanban Board</div>', unsafe_allow_html=True)
        
        if not df.empty:
            k_col1, k_col2, k_col3 = st.columns(3)
            
            with k_col1:
                st.markdown('<h4 style="color:#595959; text-align:center; padding:10px; background-color:#F3F4F6; border-radius:8px;">📋 To Do (ยังไม่เริ่ม)</h4>', unsafe_allow_html=True)
                for idx, row in df[df['Status'].isin(['ยังไม่เริ่ม', 'กำลังวางแผน'])].iterrows():
                    with st.container(border=True):
                        cat_badge = f'<span style="background-color: {get_cat_color(row["Category"])}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 11px;">{row["Category"]}</span>'
                        vis_icon = "🔒 " if "ส่วนตัว" in str(row.get('Visibility', '')) else ""
                        st.markdown(f"**{vis_icon}{row['Task']}**")
                        st.markdown(f"{cat_badge}", unsafe_allow_html=True)
                        st.caption(f"👥 {row['Assignees']} | ⏰ {row['Days Left']} วัน")
                        
                        # 🟢 แถบ Progress Bar 
                        if row['Checklist'] and row['Checklist'] != "{}":
                            try:
                                chk = json.loads(row['Checklist'])
                                if chk:
                                    done_cnt = sum(1 for v in chk.values() if v)
                                    tot_cnt = len(chk)
                                    if tot_cnt > 0:
                                        st.progress(done_cnt/tot_cnt, text=f"✅ {done_cnt}/{tot_cnt} งานย่อย")
                            except: pass
                            
                        c_btn1, c_btn2 = st.columns(2)
                        if c_btn1.button("👉 Doing", key=f"kb_doing_{idx}", use_container_width=True):
                            global_df.at[idx, 'Status'] = 'ลงมือทำ'
                            if pd.isna(global_df.at[idx, 'เริ่มทำวันที่']): global_df.at[idx, 'เริ่มทำวันที่'] = pd.Timestamp.now().replace(second=0, microsecond=0)
                            logs = json.loads(global_df.at[idx, 'Audit_Log']) if pd.notna(global_df.at[idx, 'Audit_Log']) else []
                            logs.append(create_log("ย้ายสถานะเป็น ⏳ Doing"))
                            global_df.at[idx, 'Audit_Log'] = json.dumps(logs, ensure_ascii=False)
                            save_data(global_df, DATA_FILE); st.rerun()
                        # 🟢 ปุ่ม Clone คัดลอกงานด่วน
                        if c_btn2.button("📑 Clone", key=f"kb_clone_td_{idx}", use_container_width=True):
                            cloned_task = global_df.loc[idx].copy()
                            cloned_task['วันที่เพิ่มงาน'] = pd.Timestamp.now().replace(second=0, microsecond=0)
                            cloned_task['Task'] = f"{cloned_task['Task']} (Copy)"
                            cloned_task['Status'] = 'ยังไม่เริ่ม'
                            cloned_task['เริ่มทำวันที่'] = pd.NaT
                            cloned_task['ทำถึงวันที่'] = pd.NaT
                            try:
                                chk_clone = json.loads(cloned_task['Checklist'])
                                for k in chk_clone: chk_clone[k] = False
                                cloned_task['Checklist'] = json.dumps(chk_clone)
                            except: pass
                            cloned_task['Audit_Log'] = json.dumps([create_log("คัดลอกโปรเจกต์ (Clone)")], ensure_ascii=False)
                            global_df = pd.concat([global_df, pd.DataFrame([cloned_task])], ignore_index=True)
                            save_data(global_df, DATA_FILE); st.rerun()
            
            with k_col2:
                st.markdown('<h4 style="color:#9C6500; text-align:center; padding:10px; background-color:#FFF3E0; border-radius:8px;">⏳ Doing (กำลังทำ)</h4>', unsafe_allow_html=True)
                for idx, row in df[df['Status'].isin(['ลงมือทำ', 'ติดตามผล'])].iterrows():
                    with st.container(border=True):
                        cat_badge = f'<span style="background-color: {get_cat_color(row["Category"])}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 11px;">{row["Category"]}</span>'
                        vis_icon = "🔒 " if "ส่วนตัว" in str(row.get('Visibility', '')) else ""
                        st.markdown(f"**{vis_icon}{row['Task']}**")
                        st.markdown(f"{cat_badge}", unsafe_allow_html=True)
                        st.caption(f"👥 {row['Assignees']} | ⏰ {row['Days Left']} วัน")
                        
                        # 🟢 แถบ Progress Bar
                        if row['Checklist'] and row['Checklist'] != "{}":
                            try:
                                chk = json.loads(row['Checklist'])
                                if chk:
                                    done_cnt = sum(1 for v in chk.values() if v)
                                    tot_cnt = len(chk)
                                    if tot_cnt > 0:
                                        st.progress(done_cnt/tot_cnt, text=f"✅ {done_cnt}/{tot_cnt} งานย่อย")
                            except: pass
                            
                        c_btn1, c_btn2 = st.columns(2)
                        if c_btn1.button("👈 To Do", key=f"kb_back_{idx}", use_container_width=True):
                            global_df.at[idx, 'Status'] = 'ยังไม่เริ่ม'
                            logs = json.loads(global_df.at[idx, 'Audit_Log']) if pd.notna(global_df.at[idx, 'Audit_Log']) else []
                            logs.append(create_log("ย้ายสถานะกลับเป็น 📋 To Do"))
                            global_df.at[idx, 'Audit_Log'] = json.dumps(logs, ensure_ascii=False)
                            save_data(global_df, DATA_FILE); st.rerun()
                        if c_btn2.button("✅ Done", key=f"kb_done_{idx}", use_container_width=True):
                            global_df.at[idx, 'Status'] = 'เสร็จเรียบร้อย'
                            global_df.at[idx, 'ทำถึงวันที่'] = pd.Timestamp.now().replace(second=0, microsecond=0)
                            logs = json.loads(global_df.at[idx, 'Audit_Log']) if pd.notna(global_df.at[idx, 'Audit_Log']) else []
                            logs.append(create_log("ติ๊กงาน ✅ เสร็จเรียบร้อย"))
                            global_df.at[idx, 'Audit_Log'] = json.dumps(logs, ensure_ascii=False)
                            save_data(global_df, DATA_FILE); st.rerun()
                        
                        # 🟢 ปุ่ม Clone 
                        if st.button("📑 Clone", key=f"kb_clone_do_{idx}", use_container_width=True):
                            cloned_task = global_df.loc[idx].copy()
                            cloned_task['วันที่เพิ่มงาน'] = pd.Timestamp.now().replace(second=0, microsecond=0)
                            cloned_task['Task'] = f"{cloned_task['Task']} (Copy)"
                            cloned_task['Status'] = 'ยังไม่เริ่ม'
                            cloned_task['เริ่มทำวันที่'] = pd.NaT
                            cloned_task['ทำถึงวันที่'] = pd.NaT
                            try:
                                chk_clone = json.loads(cloned_task['Checklist'])
                                for k in chk_clone: chk_clone[k] = False
                                cloned_task['Checklist'] = json.dumps(chk_clone)
                            except: pass
                            cloned_task['Audit_Log'] = json.dumps([create_log("คัดลอกโปรเจกต์ (Clone)")], ensure_ascii=False)
                            global_df = pd.concat([global_df, pd.DataFrame([cloned_task])], ignore_index=True)
                            save_data(global_df, DATA_FILE); st.rerun()
            
            with k_col3:
                st.markdown('<h4 style="color:#006100; text-align:center; padding:10px; background-color:#E8F5E9; border-radius:8px;">✅ Done (เสร็จเรียบร้อย)</h4>', unsafe_allow_html=True)
                for idx, row in df[df['Status'] == 'เสร็จเรียบร้อย'].iterrows():
                    with st.container(border=True):
                        cat_badge = f'<span style="background-color: {get_cat_color(row["Category"])}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 11px;">{row["Category"]}</span>'
                        vis_icon = "🔒 " if "ส่วนตัว" in str(row.get('Visibility', '')) else ""
                        st.markdown(f"~~**{vis_icon}{row['Task']}**~~")
                        st.markdown(f"{cat_badge}", unsafe_allow_html=True)
                        st.caption(f"👥 {row['Assignees']}")
                        
                        # 🟢 Progress Bar
                        if row['Checklist'] and row['Checklist'] != "{}":
                            try:
                                chk = json.loads(row['Checklist'])
                                if chk:
                                    done_cnt = sum(1 for v in chk.values() if v)
                                    tot_cnt = len(chk)
                                    if tot_cnt > 0:
                                        st.progress(done_cnt/tot_cnt, text=f"✅ {done_cnt}/{tot_cnt} งานย่อย")
                            except: pass
                            
                        c_btn1, c_btn2 = st.columns(2)
                        if c_btn1.button("↩️ Undo", key=f"kb_undo_{idx}", use_container_width=True):
                            global_df.at[idx, 'Status'] = 'ลงมือทำ'
                            global_df.at[idx, 'ทำถึงวันที่'] = pd.NaT
                            logs = json.loads(global_df.at[idx, 'Audit_Log']) if pd.notna(global_df.at[idx, 'Audit_Log']) else []
                            logs.append(create_log("ยกเลิกสถานะ ทำต่อ (Undo)"))
                            global_df.at[idx, 'Audit_Log'] = json.dumps(logs, ensure_ascii=False)
                            save_data(global_df, DATA_FILE); st.rerun()
                        # 🟢 ปุ่ม Clone 
                        if c_btn2.button("📑 Clone", key=f"kb_clone_dn_{idx}", use_container_width=True):
                            cloned_task = global_df.loc[idx].copy()
                            cloned_task['วันที่เพิ่มงาน'] = pd.Timestamp.now().replace(second=0, microsecond=0)
                            cloned_task['Task'] = f"{cloned_task['Task']} (Copy)"
                            cloned_task['Status'] = 'ยังไม่เริ่ม'
                            cloned_task['เริ่มทำวันที่'] = pd.NaT
                            cloned_task['ทำถึงวันที่'] = pd.NaT
                            try:
                                chk_clone = json.loads(cloned_task['Checklist'])
                                for k in chk_clone: chk_clone[k] = False
                                cloned_task['Checklist'] = json.dumps(chk_clone)
                            except: pass
                            cloned_task['Audit_Log'] = json.dumps([create_log("คัดลอกโปรเจกต์ (Clone)")], ensure_ascii=False)
                            global_df = pd.concat([global_df, pd.DataFrame([cloned_task])], ignore_index=True)
                            save_data(global_df, DATA_FILE); st.rerun()
        else: st.info("ยังไม่มีข้อมูลงาน นำไปแสดงผลบนบอร์ดครับ")

    with tab5:
        st.markdown('<div class="table-header">🧠 มุมมองวิเคราะห์แบบ Matrix (Eisenhower Matrix)</div>', unsafe_allow_html=True)
        
        if not df.empty:
            active_df = df[df['Status'] != 'เสร็จเรียบร้อย']
            q1_df = active_df[(active_df['Priority'] == 'สูง') & (active_df['Days Left'] <= 3)]
            q2_df = active_df[(active_df['Priority'] == 'สูง') & (active_df['Days Left'] > 3)]
            q3_df = active_df[(active_df['Priority'] != 'สูง') & (active_df['Days Left'] <= 3)]
            q4_df = active_df[(active_df['Priority'] != 'สูง') & (active_df['Days Left'] > 3)]

            m_col1, m_col2 = st.columns(2)
            
            with m_col1:
                html_q1 = '<div class="matrix-box matrix-q1"><h3 style="margin-top:0; color:#333;">🔥 1. ทำทันที! (Do First)</h3>'
                html_q1 += '<p style="color:#555; font-size:14px;"><em>*งานที่สำคัญและเร่งด่วน ต้องลงมือทำวันนี้*</em></p>'
                if not q1_df.empty:
                    html_q1 += '<ul style="color:#333; line-height: 1.8;">'
                    for _, row in q1_df.iterrows(): 
                        bdg = f"<span style='background-color:{get_cat_color(row['Category'])}; color:white; padding:2px 6px; border-radius:8px; font-size:10px;'>{row['Category']}</span>"
                        vis_icon = "🔒 " if "ส่วนตัว" in str(row.get('Visibility', '')) else ""
                        html_q1 += f"<li>{bdg} <strong>{vis_icon}{row['Task']}</strong> (เหลือ {row['Days Left']} วัน) <span style='font-size:11px; color:#888;'>[{row['Assignees']}]</span></li>"
                    html_q1 += '</ul>'
                else: html_q1 += '<p style="color:green;">✅ ไม่มีงานเร่งด่วนที่ต้องทำทันที</p>'
                html_q1 += '</div>'
                st.markdown(html_q1, unsafe_allow_html=True)

                html_q3 = '<div class="matrix-box matrix-q3"><h3 style="margin-top:0; color:#333;">⚡ 3. จัดการด่วน (Delegate / Quick Win)</h3>'
                if not q3_df.empty:
                    html_q3 += '<ul style="color:#333; line-height: 1.8;">'
                    for _, row in q3_df.iterrows(): 
                        bdg = f"<span style='background-color:{get_cat_color(row['Category'])}; color:white; padding:2px 6px; border-radius:8px; font-size:10px;'>{row['Category']}</span>"
                        vis_icon = "🔒 " if "ส่วนตัว" in str(row.get('Visibility', '')) else ""
                        html_q3 += f"<li>{bdg} {vis_icon}{row['Task']} (เหลือ {row['Days Left']} วัน) <span style='font-size:11px; color:#888;'>[{row['Assignees']}]</span></li>"
                    html_q3 += '</ul>'
                else: html_q3 += '<p style="color:#333;">ไม่มีข้อมูล</p>'
                html_q3 += '</div>'
                st.markdown(html_q3, unsafe_allow_html=True)

            with m_col2:
                html_q2 = '<div class="matrix-box matrix-q2"><h3 style="margin-top:0; color:#333;">📅 2. วางแผนไว้ (Schedule)</h3>'
                if not q2_df.empty:
                    html_q2 += '<ul style="color:#333; line-height: 1.8;">'
                    for _, row in q2_df.iterrows(): 
                        bdg = f"<span style='background-color:{get_cat_color(row['Category'])}; color:white; padding:2px 6px; border-radius:8px; font-size:10px;'>{row['Category']}</span>"
                        vis_icon = "🔒 " if "ส่วนตัว" in str(row.get('Visibility', '')) else ""
                        html_q2 += f"<li>{bdg} <strong>{vis_icon}{row['Task']}</strong> (กำหนดส่ง: {row['Due Date']}) <span style='font-size:11px; color:#888;'>[{row['Assignees']}]</span></li>"
                    html_q2 += '</ul>'
                else: html_q2 += '<p style="color:#333;">ไม่มีข้อมูล</p>'
                html_q2 += '</div>'
                st.markdown(html_q2, unsafe_allow_html=True)

                html_q4 = '<div class="matrix-box matrix-q4"><h3 style="margin-top:0; color:#333;">🧊 4. ทำทีหลัง (Later / Don\'t Do)</h3>'
                if not q4_df.empty:
                    html_q4 += '<ul style="color:#333; line-height: 1.8;">'
                    for _, row in q4_df.iterrows(): 
                        bdg = f"<span style='background-color:{get_cat_color(row['Category'])}; color:white; padding:2px 6px; border-radius:8px; font-size:10px;'>{row['Category']}</span>"
                        vis_icon = "🔒 " if "ส่วนตัว" in str(row.get('Visibility', '')) else ""
                        html_q4 += f"<li>{bdg} {vis_icon}{row['Task']} (เหลือ {row['Days Left']} วัน) <span style='font-size:11px; color:#888;'>[{row['Assignees']}]</span></li>"
                    html_q4 += '</ul>'
                else: html_q4 += '<p style="color:#333;">ไม่มีข้อมูล</p>'
                html_q4 += '</div>'
                st.markdown(html_q4, unsafe_allow_html=True)
        else:
            st.info("ยังไม่มีข้อมูลงานในระบบ")

    with tab6:
        st.markdown('<div class="table-header">📊 มุมมองไทม์ไลน์โปรเจกต์ (Gantt Chart)</div>', unsafe_allow_html=True)
        
        if not df.empty:
            gantt_df = df[df['Status'] != 'เสร็จเรียบร้อย'].copy()
            if not gantt_df.empty:
                gantt_df['Start_Date'] = gantt_df['เริ่มทำวันที่'].fillna(gantt_df['วันที่เพิ่มงาน'])
                gantt_df['End_Date'] = pd.to_datetime(gantt_df['Due Date'], errors='coerce')
                gantt_df = gantt_df.dropna(subset=['End_Date'])
                
                if not gantt_df.empty:
                    gantt_df.loc[gantt_df['Start_Date'] == gantt_df['End_Date'], 'End_Date'] += timedelta(days=1)
                    gantt_df['Display_Task'] = gantt_df.apply(lambda x: "🔒 " + str(x['Task']) if "ส่วนตัว" in str(x.get('Visibility', '')) else str(x['Task']), axis=1)
                    
                    fig_gantt = px.timeline(gantt_df, x_start="Start_Date", x_end="End_Date", y="Display_Task", color="Priority", 
                                            color_discrete_map={"สูง": "#FF4B4B", "ปานกลาง": "#F6B26B", "ต่ำ": "#6AA84F"},
                                            hover_name="Task", hover_data={"Assignees": True, "Status": True})
                    
                    fig_gantt.update_yaxes(autorange="reversed", title="Task") 
                    fig_gantt.update_layout(height=400, margin=dict(t=30, b=10, l=10, r=10), paper_bgcolor="rgba(0,0,0,0)")
                    st.plotly_chart(fig_gantt, use_container_width=True)
                else:
                    st.info("งานที่กำลังทำอยู่ ยังไม่มีการกำหนด Deadline ครับ")
            else:
                st.success("ไม่มีงานค้างในระบบแล้วครับ เยี่ยมมาก!")
        else:
            st.info("ยังไม่มีข้อมูลงานในระบบ")

    with tab7:
        st.markdown('<div class="table-header">📈 วิเคราะห์ประสิทธิภาพ & รายงาน (Analytics & Reports)</div>', unsafe_allow_html=True)
        
        public_global_df = global_df[~global_df['Visibility'].astype(str).str.contains("ส่วนตัว")]
        
        col_radar, col_report = st.columns([1, 1])
        
        with col_radar:
            st.markdown("#### 🕸️ เรดาร์ภาระงานทีม (Team Workload Radar)")
            st.write("ตรวจสอบภาระงานทีม (ซ่อนโปรเจกต์ 'ส่วนตัว') เพื่อป้องกันภาระงานล้นมือ")
            
            if not public_global_df.empty:
                active_tasks = public_global_df[public_global_df['Status'] != 'เสร็จเรียบร้อย']
                user_counts = {u: 0 for u in all_users_list}
                for _, row in active_tasks.iterrows():
                    assigns = [a.strip() for a in str(row['Assignees']).split(",")]
                    for a in assigns:
                        if a in user_counts:
                            user_counts[a] += 1
                
                radar_df = pd.DataFrame(list(user_counts.items()), columns=['User', 'Tasks'])
                
                if not radar_df.empty and radar_df['Tasks'].sum() > 0:
                    if len(user_counts) < 3:
                        fig_workload = px.bar(radar_df, x='User', y='Tasks', color='User', title="จำนวนงานค้างของแต่ละบุคคล")
                    else:
                        fig_workload = px.line_polar(radar_df, r='Tasks', theta='User', line_close=True, markers=True, title="ภาระงาน (Workload)")
                        fig_workload.update_traces(fill='toself', line_color='#8064A2')
                        
                    fig_workload.update_layout(margin=dict(t=30, b=30, l=30, r=30))
                    st.plotly_chart(fig_workload, use_container_width=True)
                else:
                    st.success("🎉 ตอนนี้ไม่มีงานค้างของทีมเลยครับ!")
            else:
                st.info("ยังไม่มีข้อมูลงานส่วนรวมในระบบ")

        with col_report:
            st.markdown("#### 📄 สร้างรายงานสัปดาห์อัตโนมัติ (Weekly Report)")
            st.write("กดปุ่มด้านล่างเพื่อสรุปยอดงานใน 7 วันที่ผ่านมา แล้วคัดลอกไปส่งทีมได้ทันที")
            
            if st.button("🔄 สร้างรายงานสรุปผล (Generate Report)", type="primary"):
                last_week_ts = pd.Timestamp.now().normalize() - timedelta(days=7)
                
                if not public_global_df.empty:
                    done_this_week_df = public_global_df[(public_global_df['Status'] == 'เสร็จเรียบร้อย') & 
                                                         (pd.to_datetime(public_global_df['ทำถึงวันที่'], errors='coerce') >= last_week_ts)]
                    pending_df = public_global_df[public_global_df['Status'] != 'เสร็จเรียบร้อย']
                    overdue_df = pending_df[(pd.to_datetime(pending_df['Due Date'], errors='coerce') - pd.Timestamp.now().normalize()).dt.days < 0]
                    
                    top_performer = "-"
                    if not done_this_week_df.empty:
                        done_users = []
                        for _, row in done_this_week_df.iterrows():
                            done_users.extend([u.strip() for u in str(row['Assignees']).split(",")])
                        
                        if done_users:
                            user_counts_series = pd.Series(done_users).value_counts()
                            top_user = user_counts_series.index[0]  
                            top_count = user_counts_series.iloc[0]  
                            top_performer = f"{top_user} ({top_count} งาน)"
                            
                    report_text = f"""📊 **รายงานสรุปประจำสัปดาห์ของทีม ({last_week_ts.strftime('%d/%m/%Y')} - {pd.Timestamp.now().strftime('%d/%m/%Y')})**

✅ **งานของทีมที่ทำเสร็จในสัปดาห์นี้:** {len(done_this_week_df)} งาน
⚠️ **งานของทีมที่กำลังทำอยู่ทั้งหมด:** {len(pending_df)} งาน
🚨 **งานของทีมที่เลยกำหนด (Overdue):** {len(overdue_df)} งาน

🏆 **ดาวเด่นประจำสัปดาห์ (เคลียร์งานเยอะสุด):** {top_performer}

💡 *สรุปโดยระบบ Smart To-Do Dashboard (ไม่นับรวมงานส่วนตัว)*
"""
                    st.info(report_text)
                    st.caption("สามารถคลุมดำข้อความด้านบนเพื่อ คัดลอก (Copy) นำไปส่งต่อได้เลยครับ")
                else:
                    st.warning("ยังไม่มีข้อมูลงานส่วนรวมในระบบเพื่อสร้างรายงานครับ")
