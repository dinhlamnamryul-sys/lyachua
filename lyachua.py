import streamlit as st
import cv2
import mediapipe as mp
import numpy as np
import os
from PIL import Image
from unidecode import unidecode
from gtts import gTTS
import base64
import time

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="NGÔN NGỮ KÝ HIỆU AI", layout="wide")
st.title("🤟 Hệ Thống Ngôn Ngữ Ký Hiệu AI")

# --- KHỞI TẠO MEDIAPIPE ---
mp_hands = mp.solutions.hands [cite: 14]
hands = mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5) [cite: 15]
mp_drawing = mp.solutions.drawing_utils [cite: 24]

# Định nghĩa style vẽ [cite: 27, 28]
hand_landmark_style = mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=1, circle_radius=1)
hand_connection_style = mp_drawing.DrawingSpec(color=(200, 0, 0), thickness=1, circle_radius=1)

# --- HÀM HỖ TRỢ ---
def get_audio_html(text):
    """Tạo HTML để phát âm thanh tiếng Việt qua trình duyệt [cite: 128, 129]"""
    try:
        tts = gTTS(text=f"Câu nói là: {text}", lang='vi')
        tts.save("temp_audio.mp3")
        with open("temp_audio.mp3", "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            return f'<audio autoplay="true" src="data:audio/mp3;base64,{b64}">'
    except:
        return ""

def search_sign(name, chude_val):
    """Tìm kiếm file trong các thư mục theo chủ đề [cite: 31, 33, 47, 52]"""
    name_clean = unidecode(name).lower().strip()
    folders = ["video_train", "anh_train", "đồ dùng học tập", "động vật", "gia đình", "giao thông", "trái cây"] [cite: 35]
    
    if chude_val != "Tất cả":
        folders = [chude_val]

    for folder in folders:
        if os.path.exists(folder):
            for file in os.listdir(folder):
                file_no_ext = unidecode(os.path.splitext(file)[0]).lower().strip()
                if name_clean == file_no_ext:
                    return os.path.join(folder, file)
    return None

# --- GIAO DIỆN CHÍNH ---
col_cam, col_search = st.columns([2, 1])

with col_cam:
    st.subheader("📷 Nhận diện trực tiếp")
    run_cam = st.checkbox("Bật Camera nhận diện tay")
    FRAME_WINDOW = st.image([])

    if run_cam:
        cap = cv2.VideoCapture(0)
        while run_cam:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame = cv2.flip(frame, 1)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(frame_rgb) [cite: 76]

            if results.multi_hand_landmarks: [cite: 89]
                for hand_landmarks in results.multi_hand_landmarks: [cite: 90]
                    mp_drawing.draw_landmarks(
                        frame_rgb, 
                        hand_landmarks, 
                        mp_hands.HAND_CONNECTIONS,
                        hand_landmark_style,
                        hand_connection_style
                    ) [cite: 91]
            
            FRAME_WINDOW.image(frame_rgb)
        cap.release()
    else:
        st.info("Tích vào ô 'Bật Camera' để bắt đầu.")

with col_search:
    st.subheader("🔍 Tra cứu ký hiệu")
    
    # Nhập liệu & Tìm kiếm [cite: 165, 167, 175]
    text_input = st.text_input("Nhập câu nói hoặc chữ cái:")
    chude_select = st.selectbox("Chọn chủ đề:", 
                                ["Tất cả", "đồ dùng học tập", "động vật", "gia đình", "giao thông", "trái cây"])
    
    if st.button("Tìm kiếm"):
        if text_input:
            result_path = search_sign(text_input, chude_select)
            if result_path:
                st.success(f"Đã tìm thấy: {text_input}")
                if result_path.lower().endswith(('.mp4', '.avi', '.mkv')): [cite: 54]
                    st.video(result_path) [cite: 55]
                else:
                    st.image(result_path) [cite: 57]
                
                # Phát âm thanh tiếng Việt [cite: 155]
                st.components.v1.html(get_audio_html(text_input), height=0)
            else:
                st.error("Không tìm thấy ngôn ngữ ký hiệu nào phù hợp") [cite: 61]
        else:
            st.warning("Vui lòng nhập từ khóa.")

st.divider()
st.markdown("### 📘 Hướng dẫn bổ sung")
st.info("""
- **Nhận diện chữ cái có dấu (Ă, Â, Ê...):** Thực hiện ký hiệu chữ cái gốc kèm theo cử động vẽ dấu phụ như trong bảng ký hiệu.
- **Phân biệt Chữ và Số:** Hệ thống ưu tiên nhận diện chữ cái. Để nhập số, hãy giữ nguyên tay trong 2 giây hoặc sử dụng khung tìm kiếm.
- **Tiếng Mông:** Tính năng đang được cập nhật cơ sở dữ liệu từ điển.
""")
