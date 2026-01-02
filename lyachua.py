import streamlit as st
import cv2
import mediapipe as mp
import numpy as np
import os
from unidecode import unidecode
from gtts import gTTS
import base64

# --- CẤU HÌNH GIAO DIỆN ---
st.set_page_config(page_title="NGÔN NGỮ KÝ HIỆU AI", layout="wide")
st.title("🤟 Hệ Thống Ngôn Ngữ Ký Hiệu AI")

# --- KHỞI TẠO CÔNG CỤ AI ---
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

# --- HÀM HỖ TRỢ ---
def play_audio_web(text):
    """Chuyển văn bản thành âm thanh và phát trên trình duyệt"""
    try:
        tts = gTTS(text=f"Câu nói là: {text}", lang='vi')
        tts.save("temp_audio.mp3")
        with open("temp_audio.mp3", "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            md = f'<audio autoplay="true" src="data:audio/mp3;base64,{b64}">'
            st.components.v1.html(md, height=0)
    except:
        pass

def search_logic(name, chude_val):
    """Logic tìm kiếm file theo chủ đề (Dựa trên code gốc)"""
    name_clean = unidecode(name).lower().strip()
    
    # Danh sách thư mục tìm kiếm [cite: 35]
    if chude_val == "Tất cả":
        folders = ["video_train", "anh_train", "đồ dùng học tập", "động vật", "gia đình", "giao thông", "trái cây"]
    else:
        folders = [chude_val]

    for folder in folders:
        if os.path.exists(folder):
            for file in os.listdir(folder):
                file_name = unidecode(os.path.splitext(file)[0]).lower().strip()
                if name_clean == file_name:
                    return os.path.join(folder, file)
    return None

# --- GIAO DIỆN CHÍNH ---
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("📷 Camera Nhận Diện")
    run_cam = st.toggle("Kích hoạt Camera")
    FRAME_PLACEHOLDER = st.empty()

    if run_cam:
        # Sử dụng index 0 cho camera mặc định
        cap = cv2.VideoCapture(0)
        while run_cam:
            ret, frame = cap.read()
            if not ret:
                st.error("Không thể kết nối Camera.")
                break
            
            # Xử lý hình ảnh [cite: 73, 76]
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb_frame)

            # Vẽ điểm mốc tay [cite: 91, 92]
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(
                        rgb_frame, 
                        hand_landmarks, 
                        mp_hands.HAND_CONNECTIONS
                    )
            
            FRAME_PLACEHOLDER.image(rgb_frame, channels="RGB")
        cap.release()
    else:
        st.info("Gạt nút phía trên để bắt đầu sử dụng Camera.")

with col_right:
    st.subheader("🔍 Tra cứu từ điển")
    input_text = st.text_input("Nhập chữ cái hoặc từ cần tra:")
    option = st.selectbox("Chủ đề:", ["Tất cả", "đồ dùng học tập", "động vật", "gia đình", "giao thông", "trái cây"])
    
    if st.button("Tìm kiếm"):
        if input_text:
            path = search_logic(input_text, option)
            if path:
                st.success(f"Kết quả cho: {input_text}")
                if path.lower().endswith(('.mp4', '.avi', '.mkv')):
                    st.video(path)
                else:
                    st.image(path)
                play_audio_web(input_text)
            else:
                st.warning("Không tìm thấy dữ liệu phù hợp.")

st.divider()
st.info("**Lưu ý:** Để nhận diện Ă, Â, Ê, Ô, Ơ, Ư, hãy thực hiện ký hiệu chữ cái gốc kèm theo dấu phụ tương ứng như trong tài liệu hướng dẫn.")
