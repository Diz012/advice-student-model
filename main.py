import os
import json
from fastapi import FastAPI
from pydantic import BaseModel
from groq import Groq
from datetime import datetime, timedelta

app = FastAPI()

# Cấu hình Client Groq (Sử dụng biến môi trường để bảo mật)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Định nghĩa cấu trúc dữ liệu đầu vào
class StudentProfile(BaseModel):
    mssv: str
    nganh: str
    ly_do_rot: str

def get_hard_logic_advice(profile: StudentProfile):
    """Xử lý các lời khuyên dựa trên điều kiện cứng bạn yêu cầu"""
    advices = []
    
    # 1. Điểm chuyên cần thấp
    if "chuyên cần" in profile.ly_do_rot.lower():
        advices.append("Bạn đang có mức độ chuyên cần thấp. Hãy cố gắng sắp xếp thời gian để tham dự đầy đủ các buổi học còn lại nhằm cải thiện điểm quá trình và nắm vững kiến thức.")

    # 2. Đóng trễ học phí & Học bổng
    if "trễ học phí" in profile.ly_do_rot.lower():
        advices.append(f"Do bạn đã trễ học phí nên sẽ không có điểm quá trình, vì vậy hãy cố gắng thi thật tốt để bị rớt môn.")
    # 3. Ít tham gia học nhóm
    if "học nhóm" in profile.ly_do_rot.lower():
        advices.append(f"Việc học nhóm sẽ giúp bạn tiến bộ nhanh hơn. Hãy tham khảo các câu lạc bộ học thuật tại liên quan ngành {profile.nganh} để tìm kiếm cộng đồng cùng học tập nhé.")

    return " ".join(advices)

@app.post("/consult")
async def student_consultant(profile: StudentProfile):
    # Lấy lời khuyên từ logic hệ thống trước
    system_advice = get_hard_logic_advice(profile)
    
    # Dùng AI để viết lại lời khuyên cho tự nhiên và cá nhân hóa
    prompt = f"""
        Bạn là một cố vấn học tập tận tâm. Hãy viết một bức thư ngắn hoặc lời nhắn gửi đến sinh viên dựa trên thông tin sau:
        - MSSV: {profile.mssv}
        - Ngành: {profile.nganh}
        - Lý do rớt môn: {profile.ly_do_rot}
        - Các giải pháp gợi ý: {system_advice}
        
        Yêu cầu: 
        1. Giọng văn động viên, chuyên nghiệp.
        2. Đưa ra các giải pháp phù hợp với {system_advice}.
        3. Đưa ra thêm lời khuyên về cách cải thiện dựa trên hướng giải quyết thông thường của các trường đại học.
        4. Định dạng JSON nghiêm ngặt.
        (Sẽ có những lý do rớt môn khiến hệ thống không đưa ra được giải pháp gợi ý, hãy tạo ra các giải pháp phù hợp cho lý do này dự trên các cách giải quyết hoặc quy định thuộc các trường đại học tại Việt Nam)

        Yêu cầu trả về duy nhất một đối tượng JSON có cấu trúc như sau:
        {{
            "mssv": {profile.mssv},
            "loi_khuyen": "Giải pháp đưa ra để gợi ý cho sinh viên"
        }}
    """

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(completion.choices[0].message.content)
    except Exception as e:
        return {"error": str(e), "fallback_advice": system_advice}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
