import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import os
import calendar

# --- 1. ตั้งค่าหน้าเพจ ---
st.set_page_config(page_title="Smart To-Do Dashboard", layout="wide")

# ฝัง CSS สไตล์สีม่วง
st.markdown("""
    <style>
    .metric-card {
        background-color: #ffffff;
        border: 2px solid #8064A2;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        color: #333333;
    }
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
    </style>
""", unsafe_allow_html=True)

# --- 2. ฟังก์ชันจัดการข้อมูลหมวดหมู่ (Categories) ---
CAT_FILE = "categories.csv"
def load_categories():
    if os.path.exists(CAT_FILE):
        cats = pd.read_csv(CAT_FILE)['Category'].dropna().tolist()
        return [c for c in cats if str(c).strip() != ""] # กรองค่าว่างออก
    else:
        defaults = ["ระบบ / ไอที", "งาน R&D", "บ้าน & DIY", "ตู้ปลา", "ทั่วไป"]
        pd.DataFrame({"Category": defaults}).to_csv(CAT_FILE, index=False)
        return defaults

def save_categories(cat_list):
    pd.DataFrame({"Category": cat_list}).to_csv(CAT_FILE, index=False)

# --- 3. ฟังก์ชันจัดการข้อมูลงาน (Tasks) ---
DATA_FILE = "tasks.csv"
def load_data(all_categories):
    today = datetime.now().date()
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        # ตรวจสอบคอลัมน์และเติมค่าเริ่มต้นหากมีค่าว่าง (ป้องกัน Error ในตาราง)
        if 'Category' in df.columns: df['Category'] = df['Category'].fillna(all_categories[0] if all_categories else "ทั่วไป")
        if 'Priority' in df.columns: df['Priority'] = df['Priority'].fillna("ต่ำ")
        if 'Status' in df.columns: df['Status'] = df['Status'].fillna("ยังไม่เริ่ม")
        
        for col in ['วันที่เพิ่มงาน', 'เริ่มทำวันที่', 'ทำถึงวันที่']:
            if col not in df.columns: df[col] = None
        
        for col in ['วันที่เพิ่มงาน', 'Due Date', 'เริ่มทำวันที่', 'ทำถึงวันที่']:
            df[col] = pd.to_datetime(df[col], errors='coerce').dt.date
    else:
        data = {
            "วันที่เพิ่มงาน": [today],
            "Task": ["ตัวอย่างงาน"],
            "Category": [all_categories[0] if all_categories else "ทั่วไป"],
            "Priority": ["ต่ำ"],
            "Due Date": [today + timedelta(days=1)],
            "เริ่มทำวันที่": [None], "ทำถึงวันที่": [None],
            "Status": ["ยังไม่เริ่ม"]
        }
        df = pd.DataFrame(data)
    return df

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# โหลดข้อมูล
all_categories = load_categories()
df = load_data(all_categories)

# --- 4. Sidebar ---
with st.sidebar:
    st.header("⚙️ ตั้งค่าหมวดหมู่")
    new_cat_input = st.text_input("เพิ่มประเภทงานใหม่")
    if st.button("➕ เพิ่มหมวดหมู่"):
        if new_cat_input and new_cat_input not in all_categories:
            all_categories.append(new_cat_input)
            save_categories(all_categories)
            st.rerun()

    st.markdown("---")
    st.subheader("รายการหมวดหมู่")
    for i, cat in enumerate(all_categories):
        c_col1, c_col2 = st.columns([3, 1])
        c_col1.write(cat)
        if c_col2.button("🗑️", key=f"del_{i}"):
            all_categories.remove(cat)
            save_categories(all_categories)
            st.rerun()

# ส่วนหัว
st.title("🎯 Smart To-Do List Dashboard")
st.markdown("---")

# คำนวณ Days Left
df['ลำดับ'] = range(1, len(df) + 1)
today_ts = pd.Timestamp.now().normalize()
df['Days Left'] = (pd.to_datetime(df['Due Date']) - today_ts).dt.days

# จัดลำดับคอลัมน์
column_order = ['ลำดับ', 'วันที่เพิ่มงาน', 'Task', 'Category', 'Priority', 'Due Date', 'Days Left', 'เริ่มทำวันที่', 'ทำถึงวันที่', 'Status']
df = df[[col for col in column_order if col in df.columns]]

# --- 5. Tabs ---
tab1, tab2 = st.tabs(["📊 Dashboard & Tasks", "📅 Calendar View"])

with tab1:
    total_tasks = len(df)
    completed_tasks = len(df[df['Status'] == "เสร็จเรียบร้อย"])
    pending_tasks = total_tasks - completed_tasks
    near_deadline = len(df[(df['Status'] != "เสร็จเรียบร้อย") & (df['Days Left'] <= 3) & (df['Days Left'] >= 0)])

    left_col, right_col = st.columns([2, 1])
    with left_col:
        c1, c2 = st.columns(2)
        with c1: st.markdown(f"""<div class="metric-card"><div class="metric-title">📝 งานทั้งหมด</div><div class="metric-value">{total_tasks}</div><div class="metric-subtitle">ทั้งหมด (งาน)</div></div>""", unsafe_allow_html=True)
        with c2: st.markdown(f"""<div class="metric-card"><div class="metric-title">✅ งานเสร็จแล้ว</div><div class="metric-value">{completed_tasks}</div><div class="metric-subtitle">เสร็จแล้ว (งาน)</div></div>""", unsafe_allow_html=True)
        c3, c4 = st.columns(2)
        with c3: st.markdown(f"""<div class="metric-card"><div class="metric-title">⚠️ งานค้าง</div><div class="metric-value">{pending_tasks}</div><div class="metric-subtitle">ค้าง (งาน)</div></div>""", unsafe_allow_html=True)
        with c4: st.markdown(f"""<div class="metric-card"><div class="metric-title">⏰ งานใกล้ Deadline</div><div class="metric-value">{near_deadline}</div><div class="metric-subtitle">ภายใน 3 วัน (งาน)</div></div>""", unsafe_allow_html=True)

    with right_col:
        st.markdown("""<div style="text-align: center; color: #8064A2; font-size: 20px; font-weight: bold; margin-bottom: 10px;">ความคืบหน้ารวม</div>""", unsafe_allow_html=True)
        if total_tasks > 0:
            pct = int((completed_tasks/total_tasks)*100)
            fig = px.pie(values=[completed_tasks, pending_tasks], names=["เสร็จแล้ว", "ยังไม่เสร็จ"], hole=0.6, color_discrete_sequence=["#8064A2", "#D9D9D9"])
            fig.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=260, showlegend=False, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", annotations=[dict(text=f"{pct}%", x=0.5, y=0.5, font_size=40, showarrow=False, font_color="#604A7B")])
            st.plotly_chart(fig, use_container_width=True)
            st.markdown(f"""<div style="text-align: center; color: #888; font-size: 16px; margin-top: -20px;">เสร็จแล้ว <span style="font-weight: bold; color: #8064A2;">{completed_tasks}</span> จาก <span style="font-weight: bold; color: #8064A2;">{total_tasks}</span> งาน</div>""", unsafe_allow_html=True)
        else: st.info("ยังไม่มีข้อมูลงาน")

    st.markdown("---")

    with st.expander("➕ เพิ่มงานใหม่ (คลิกเพื่อขยาย)"):
        with st.form("add_task_form"):
            c1, c2, c3 = st.columns(3)
            new_task = c1.text_input("ชื่อภารกิจ / งาน")
            new_cat = c2.selectbox("ประเภทงาน", all_categories)
            new_pri = c3.selectbox("ความสำคัญ", ["สูง", "ปานกลาง", "ต่ำ"], index=2) # Default ต่ำ
            c4, c5, c6 = st.columns(3)
            new_due = c4.date_input("วันที่ Deadline", format="DD/MM/YYYY")
            new_stat = c5.selectbox("สถานะ", ["ยังไม่เริ่ม", "กำลังวางแผน", "ลงมือทำ", "ติดตามผล", "เสร็จเรียบร้อย"], index=0)
            
            if st.form_submit_button("บันทึกงาน") and new_task:
                new_row = pd.DataFrame([{
                    "วันที่เพิ่มงาน": datetime.now().date(), "Task": new_task, "Category": new_cat, 
                    "Priority": new_pri, "Due Date": new_due, "Status": new_stat
                }])
                df = pd.concat([df, new_row], ignore_index=True)
                save_data(df)
                st.rerun()

    st.subheader("📋 รายการงานทั้งหมด")

    def highlight_days_left(val):
        if pd.isna(val): return ''
        if val <= 1: return 'background-color: #FFC7CE; color: #9C0006;'
        elif 2 <= val <= 3: return 'background-color: #FFEB9C; color: #9C6500;'
        else: return 'background-color: #C6EFCE; color: #006100;'
        
    def highlight_priority(val):
        if pd.isna(val): return ''
        val_str = str(val).strip()
        if val_str == 'สูง': return 'background-color: #FFC7CE; color: #9C0006;'
        elif val_str == 'ปานกลาง': return 'background-color: #FFEB9C; color: #9C6500;'
        elif val_str == 'ต่ำ': return 'background-color: #C6EFCE; color: #006100;'
        return ''

    styled_df = df.style.map(highlight_days_left, subset=['Days Left']).map(highlight_priority, subset=['Priority'])

    # ตั้งค่าตารางแบบ REQUIRED เพื่อไม่ให้มีตัวเลือกว่าง
    edited_df = st.data_editor(
        styled_df, 
        use_container_width=True, 
        hide_index=True,
        disabled=["ลำดับ", "วันที่เพิ่มงาน", "Days Left"], 
        column_config={
            "Task": st.column_config.TextColumn("ภารกิจ / งาน", width="large", required=True),
            "Category": st.column_config.SelectboxColumn("ประเภทงาน", options=all_categories, required=True),
            "Priority": st.column_config.SelectboxColumn("ความสำคัญ", options=["สูง", "ปานกลาง", "ต่ำ"], required=True),
            "Due Date": st.column_config.DateColumn("วันที่ Deadline", format="DD/MM/YYYY", required=True),
            "Status": st.column_config.SelectboxColumn("อัพเดทสถานะ", options=["ยังไม่เริ่ม", "กำลังวางแผน", "ลงมือทำ", "ติดตามผล", "เสร็จเรียบร้อย"], required=True)
        }
    )

    if not df.equals(edited_df):
        save_data(edited_df)
        st.rerun()

with tab2:
    st.subheader("📅 ปฏิทินงานประจำเดือน")
    today_date = datetime.now().date()
    thai_months = ["มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน", "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"]
    col_m, col_y, _ = st.columns([1, 1, 3])
    sel_m = thai_months.index(col_m.selectbox("เลือกเดือน", thai_months, index=today_date.month - 1)) + 1
    sel_y = col_y.selectbox("เลือกปี (ค.ศ.)", range(today_date.year - 1, today_date.year + 3), index=1)
    
    cal = calendar.Calendar(firstweekday=0) 
    month_days = cal.monthdatescalendar(sel_y, sel_m)

    html_cal = '<table class="cal-table"><tr>'
    for d in ["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์", "อาทิตย์"]: html_cal += f"<th class='cal-th'>{d}</th>"
    html_cal += "</tr>"
    for week in month_days:
        html_cal += "<tr>"
        for d in week:
            css = "cal-td" + (" other-month" if d.month != sel_m else "") + (" today" if d == today_date else "")
            html_cal += f"<td class='{css}'><div class='date-num'>{d.day}</div>"
            day_tasks = df[df['Due Date'] == d]
            for _, row in day_tasks.iterrows():
                badge = "task-badge done" if row['Status'] == "เสร็จเรียบร้อย" else "task-badge"
                html_cal += f"<div class='{badge}'>• {row['Task']}</div>"
            html_cal += "</td>"
    st.markdown(html_cal + "</table>", unsafe_allow_html=True)