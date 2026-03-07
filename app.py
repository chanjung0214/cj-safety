import streamlit as st
import os
import json
from datetime import datetime, date, time, timedelta
from edu_maker import SafetyEduReportGenerator  

# ---------------------------------------------------------
# 🔒 [보안 설정] 우리 현장만의 비밀번호를 정하세요!
# ---------------------------------------------------------
SITE_PASSWORD = "cj0021"  # <--- 대리님이 원하는 암호로 바꾸셔도 됩니다!
# ---------------------------------------------------------

st.set_page_config(page_title="안전교육 자동화 시스템", layout="wide")

# 세션 상태에 로그인 여부 저장
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# 🚪 [도어락 화면] 로그인이 안 되어 있으면 암호 입력창 표시
if not st.session_state.logged_in:
    st.title("🚧 창조종합건설 안전관리 시스템")
    st.info("본 시스템은 인산지구 배수개선사업 현장 전용입니다. 인증 후 이용 가능합니다.")
    
    pwd_input = st.text_input("현장 인증 암호를 입력하세요", type="password")
    if st.button("인증하기"):
        if pwd_input == SITE_PASSWORD:
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("❌ 암호가 틀렸습니다. 현장 사무실에 문의하세요.")
    st.stop() # 인증 전까지 아래 코드는 절대 실행 안 됨

# ---------------------------------------------------------
# 🔓 여기서부터는 인증 성공 시에만 보이는 메인 화면입니다.
# ---------------------------------------------------------

SETTINGS_FILE = "user_settings.json"

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {"site_name": "", "instructor": "", "start_time": "07:00", "end_time": "09:00"}

def update_setting(key, value):
    settings = load_settings()
    settings[key] = value
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f)

def update_time_setting(start, end):
    settings = load_settings()
    settings["start_time"] = start
    settings["end_time"] = end
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f)

if "files_ready" not in st.session_state:
    st.session_state.files_ready = False
    st.session_state.edu_file = ""
    st.session_state.photo_file = ""

settings = load_settings()

st.title("🚧 특별안전교육 일괄 생성 시스템")
st.write(f"접속자: {settings.get('instructor', '현장 관계자')} 님 반갑습니다.")
st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📝 교육 기본 정보")
    site_name = st.text_input("현장명", value=settings.get("site_name", ""))
    if st.checkbox("💾 기본값으로 저장", key="save_site"):
        update_setting("site_name", site_name)
        
    st.markdown("<br>", unsafe_allow_html=True)
    selected_date = st.date_input("교육 날짜", value=date.today()) 
    date_str = selected_date.strftime("%y%m%d") 
    
    st.markdown("<br>", unsafe_allow_html=True)
    instructor = st.text_input("교육 실시자", value=settings.get("instructor", ""))
    if st.checkbox("💾 기본값으로 저장", key="save_inst"):
        update_setting("instructor", instructor)
        
    st.markdown("<br>", unsafe_allow_html=True)
    count = st.text_input("교육 인원 (명)", value="")
    
    st.markdown("**⏰ 교육 시간 설정**")
    start_dt_obj = datetime.strptime(settings.get("start_time", "07:00"), "%H:%M").time()
    end_dt_obj = datetime.strptime(settings.get("end_time", "09:00"), "%H:%M").time()
    
    time_col1, time_col2 = st.columns(2)
    with time_col1:
        start_time = st.time_input("시작 시간", value=start_dt_obj)
    with time_col2:
        end_time = st.time_input("종료 시간", value=end_dt_obj)
        
    if st.checkbox("💾 기본값으로 저장", key="save_time"):
        update_time_setting(start_time.strftime("%H:%M"), end_time.strftime("%H:%M"))
    
    time_range = f"{start_time.strftime('%H:%M')}~{end_time.strftime('%H:%M')}"
    st.info(f"⏱️ 설정된 교육 시간: **{time_range}**")

with col2:
    st.subheader("📋 교육 항목 선택")
    menu_options = {
        "1": "고압실 내 작업", "2": "아세틸렌/가스집합 용접·용단 작업", "3": "밀폐/습한 장소 용접작업",
        "19": "지반굴착 안전작업 (2m 이상)", "25": "거푸집 동바리 조립·해체", "26": "비계 조립·해체·변경",
        "38": "화재위험작업 (용접, 용단 등)", "CE_1": "항타기 및 항발기 작업", "CE_2": "콘크리트 펌프카 작업"
    } # (지면상 줄임, 대리님은 41개 다 넣으시면 됩니다!)

    selected_names = st.multiselect("교육 항목 선택 (최대 5개)", list(menu_options.values()), max_selections=5)
    selected_keys = [k for k, v in menu_options.items() if v in selected_names]

    st.markdown("<br>", unsafe_allow_html=True)
    auto_content = " / ".join(selected_names) if selected_names else "특별안전교육 실시"
    content_str = st.text_input("📝 교육 내용 (사진대지용)", value=auto_content)

st.markdown("---")
st.subheader("📸 현장 사진 첨부")
photo_cols = st.columns(4)
uploaded_files = [None] * 4
for i in range(4):
    with photo_cols[i]:
        uploaded_files[i] = st.file_uploader(f"사진 {i+1}", type=['jpg', 'jpeg', 'png'], key=f"photo_{i}")
        if uploaded_files[i] is not None:
            st.image(uploaded_files[i], use_container_width=True)

if st.button("🖨️ 서류 일괄 자동 생성", use_container_width=True):
    if not selected_keys or not count:
        st.error("⚠️ 교육 항목과 인원을 입력해주세요!")
    else:
        with st.spinner("작성 중..."):
            valid_files = [f for f in uploaded_files if f is not None]
            temp_paths = []
            for idx, file in enumerate(valid_files):
                temp_path = f"upload_temp_{idx}.jpg"
                with open(temp_path, "wb") as f:
                    f.write(file.getbuffer())
                temp_paths.append(temp_path)
            
            generator = SafetyEduReportGenerator("특별안전교육_양식.xlsx", "사진대지_양식.xlsx")
            edu_file = generator.process_education(selected_keys, site_name, date_str, instructor, count, time_range)
            photo_file = generator.process_photos(date_str, content_str, temp_paths)
            
            for p in temp_paths:
                if os.path.exists(p): os.remove(p)
            
            st.session_state.edu_file, st.session_state.photo_file, st.session_state.files_ready = edu_file, photo_file, True
            st.rerun()

if st.session_state.files_ready:
    st.success("🎉 작성이 완료되었습니다!")
    dl_col1, dl_col2 = st.columns(2)
    with dl_col1:
        with open(st.session_state.edu_file, "rb") as f:
            st.download_button("📥 일지 다운로드", f, file_name=st.session_state.edu_file)
    with dl_col2:
        with open(st.session_state.photo_file, "rb") as f:
            st.download_button("📥 사진대지 다운로드", f, file_name=st.session_state.photo_file)
