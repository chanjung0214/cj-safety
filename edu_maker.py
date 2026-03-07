import openpyxl
from openpyxl.drawing.image import Image as ExcelImage
from PIL import Image as PILImage
import os

class SafetyEduReportGenerator:
    def __init__(self, edu_template, photo_template):
        self.edu_template = edu_template
        self.photo_template = photo_template

    # ⭐ [수정 완료] 현장명(site_name)을 받을 수 있도록 장착된 최신 엔진입니다!
    def process_education(self, sheet_numbers, site_name, date_str, instructor, count, time_range):
        wb = openpyxl.load_workbook(self.edu_template)
        date_korean = f"20{date_str[:2]}년 {date_str[2:4]}월 {date_str[4:]}일"
        
        for num in sheet_numbers:
            if num in wb.sheetnames:
                ws = wb[num]
                ws['C4'] = site_name    # 현장명 입력!
                ws['A3'] = date_korean  
                ws['I4'] = instructor
                ws['C6'] = f"대상( {count} 名)      참석( {count} 名)      미실시( 0 名)"
                ws['I7'] = time_range
        
        sheets_to_keep = sheet_numbers + ["서명지", "서명부"] 
        for sheet_name in wb.sheetnames:
            if sheet_name not in sheets_to_keep:
                del wb[sheet_name]
                
        save_path = f"특별안전교육_결과_{date_str}.xlsx"
        wb.save(save_path)
        return save_path 

    def process_photos(self, date_str, content_str, photo_paths):
        wb = openpyxl.load_workbook(self.photo_template)
        ws = wb.active 
        
        date_dash = f"20{date_str[:2]}-{date_str[2:4]}-{date_str[4:]}"
        ws.title = date_dash 
        
        positions = [
            {'img': 'A2',  'date': 'B21', 'content': 'E21'},
            {'img': 'A23', 'date': 'B42', 'content': 'E42'},
            {'img': 'I2',  'date': 'J21', 'content': 'M21'},
            {'img': 'I23', 'date': 'J42', 'content': 'M42'}
        ]
        
        for idx, img_path in enumerate(photo_paths):
            if idx >= 4:
                break
            
            pos = positions[idx]
            ws[pos['date']] = date_dash
            ws[pos['content']] = content_str
            
            if os.path.exists(img_path):
                img = PILImage.open(img_path)
                img = img.resize((610, 430), PILImage.Resampling.LANCZOS)
                
                temp_img_path = f"temp_{idx}.png"
                img.save(temp_img_path)
                
                excel_img = ExcelImage(temp_img_path)
                ws.add_image(excel_img, pos['img'])
        
        save_path = f"사진대지_결과_{date_str}.xlsx"
        wb.save(save_path)
        
        for f in os.listdir('.'):
            if f.startswith('temp_') and f.endswith('.png'):
                os.remove(f)
                
        return save_path

    def update_master_db(self, date_str, instructor, count, time_range, selected_names):
        db_path = "안전교육_관리대장.xlsx"
        date_korean = f"20{date_str[:2]}년 {date_str[2:4]}월 {date_str[4:]}일"
        
        if not os.path.exists(db_path):
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "교육대장"
            ws.append(["교육일자", "실시자", "교육인원(명)", "교육시간", "교육항목"])
        else:
            wb = openpyxl.load_workbook(db_path)
            ws = wb.active
            
        items_str = ", ".join(selected_names)
        ws.append([date_korean, instructor, count, time_range, items_str])
        wb.save(db_path)