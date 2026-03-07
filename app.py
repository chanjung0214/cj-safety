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

# 🚪 [도어락 화면] 엔터키 지원 버전
if not st.session_state.logged_in:
    st.title("🚧 창조종합건설 안전관리 시스템")
    st.info("본 시스템은 인산지구 배수개선사업 현장 전용입니다. 인증 후 이용 가능합니다.")
    
    # [수정] on_change를 활용해 엔터키 입력 시 바로 함수가 실행되도록 합니다.
    def check_password():
        if st.session_state.password_attempt == SITE_PASSWORD:
            st.session_state.logged_in = True
        else:
            st.error("❌ 암호가 틀렸습니다. 현장 사무실에 문의하세요.")

    st.text_input(
        "현장 인증 암호를 입력하세요", 
        type="password", 
        key="password_attempt", 
        on_change=check_password  # 엔터 치면 이 함수가 실행됩니다!
    )
    
    if st.button("인증하기"):
        check_password()
        
    st.stop()

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
        "4": "폭발성·인화성 물질 등 취급작업", "5": "가스 발생장치 취급 작업", "6": "화학설비 반응기·교반기 취급/세척",
        "7": "화학설비 탱크 내 작업", "8": "저장탱크 내부 작업", "9": "위험물 가열·건조작업",
        "10": "집재장치 조립·해체 및 운반 작업", "11": "동력 프레스기계 작업", "12": "목재가공용 기계 작업",
        "13": "운반용 등 하역기계 작업", "14": "크레인/호이스트 작업", "15": "건설용 리프트·곤돌라 작업",
        "16": "주물 및 단조 작업", "17": "75V 이상 정전/활선작업", "18": "콘크리트 파쇄기를 사용한 파쇄작업",
        "19": "지반굴착 안전작업 (2m 이상)", "20": "흙막이 지보공·동바리 작업", "21": "터널 굴착/거푸집/콘크리트 작업",
        "22": "암석 굴착작업 (2m 이상)", "23": "물건 적재/해체 작업 (2m 이상)", "24": "선박 하역/이동 작업",
        "25": "거푸집 동바리 조립·해체", "26": "비계 조립·해체·변경", "27": "건축물 골조 등 조립·해체·변경 (5m 이상)",
        "28": "목조건축물 부재 조립 등 (5m 이상)", "29": "콘크리트 인공구조물 해체/파괴 (2m 이상)", "30": "타워크레인 설치·해체",
        "31": "보일러 설치/취급", "32": "압력용기 설치/취급", "33": "방사선 업무 관계 작업",
        "34": "밀폐공간 안전작업", "35": "유해물질 제조/취급", "36": "로봇작업",
        "37": "석면 해체·제거", "38": "화재위험작업 (용접, 용단 등)", "39": "타워크레인 신호업무",
        "CE_1": "항타기 및 항발기 작업", "CE_2": "콘크리트 펌프카 작업"
    }

    full_descriptions = {
        "1": "고압실 내 작업 (대기압 초과 작업실 또는 수갱 내부)", "2": "아세틸렌 용접장치 또는 가스집합 용접장치를 사용하는 금속의 용접·용단 또는 가열작업", "3": "밀폐된 장소(탱크 내 등) 또는 습한 장소에서 하는 전기용접 작업",
        "4": "폭발성·물반응성·인화성 물질 등의 제조 또는 취급작업", "5": "인화성 가스 또는 폭발성 물질 중 가스의 발생장치 취급 작업", "6": "화학설비 중 반응기, 교반기·추출기의 사용 및 세척작업",
        "7": "화학설비의 탱크 내 작업", "8": "분말·원재료 등을 담은 호퍼·저장창고 등 저장탱크의 내부 작업", "9": "위험물 건조설비(속부피 1㎥ 이상) 등 연료/전력을 열원으로 사용하는 물건의 가열·건조작업",
        "10": "집재장치(정격출력 7.5kW 이상, 경사거리 350m 이상 등) 조립·해체 및 집재·운반 작업", "11": "동력에 의하여 작동되는 프레스기계를 5대 이상 보유한 사업장에서 해당 기계 작업", "12": "목재가공용 기계를 5대 이상 보유한 사업장에서 해당 기계 작업",
        "13": "운반용 등 하역기계를 5대 이상 보유한 사업장에서 해당 기계 작업", "14": "1톤 이상 크레인 사용 또는 1톤 미만 크레인/호이스트 5대 이상 보유 사업장 작업", "15": "건설용 리프트·곤돌라를 이용한 작업",
        "16": "주물 및 단조(금속을 두들겨 형체를 만드는 일) 작업", "17": "전압기 75V 이상 정전 및 활선작업", "18": "콘크리트 파쇄기를 사용한 파쇄작업 (2m 이상 구조물)",
        "19": "굴착면 높이 2m 이상 지반굴착 안전작업", "20": "흙막이 지보공의 보강 또는 동바리 설치·해체공사 안전작업", "21": "터널 안 굴착작업 또는 터널 거푸집 지보공 조립·콘크리트 작업",
        "22": "굴착면 높이가 2m 이상이 되는 암석의 굴착작업", "23": "높이가 2m 이상인 물건을 쌓거나 무너뜨리는 작업", "24": "선박에 짐을 쌓거나 부리거나 이동시키는 작업",
        "25": "거푸집 동바리 조립·해체공사 안전작업", "26": "비계 조립·해체 또는 변경 시 안전작업", "27": "건축물 골조, 다리 상부구조 등(5m 이상)의 조립·해체·변경작업",
        "28": "처마 높이 5m 이상 목조건축물 구조 부재 조립 및 외벽 밑 설치작업", "29": "콘크리트 인공구조물(높이 2m 이상)의 해체 또는 파괴작업", "30": "타워크레인을 설치(상승작업 포함)·해체하는 작업",
        "31": "보일러(소형 보일러 제외)의 설치 및 취급 작업", "32": "압력용기(게이지 압력 ㎡당 1kg 이상)의 설치 및 취급 작업", "33": "방사선 업무에 관계되는 작업 (의료 및 실험용 제외)",
        "34": "밀폐공간에서의 안전작업", "35": "허가 및 관리대상 유해물질의 제조 또는 취급 시 안전작업", "36": "로봇작업",
        "37": "석면 해체·제거작업", "38": "가연물이 있는 장소에서 하는 화재위험작업 (용접, 용단 등)", "39": "타워크레인을 사용하는 작업 시 신호업무를 하는 작업",
        "CE_1": "건설기계 (항타기 및 항발기 안전작업)", "CE_2": "건설기계 (콘크리트 펌프카 사용 안전작업)"
    }

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


