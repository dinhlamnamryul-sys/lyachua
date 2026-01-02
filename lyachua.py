import streamlit as st
import cv2
import mediapipe as mp
import numpy as np
import os
from unidecode import unidecode
from gtts import gTTS
import base64

# --- CẤU HÌNH MEDIAPIPE ---
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

# --- HÀM HỖ TRỢ ---
def get_audio_html(text):
    """Tạo âm thanh tiếng Việt để phát trên trình duyệt"""
    try:
        tts = gTTS(text=f"Câu nói là: {text}", lang='vi')
        tts.save("temp_audio.mp3")
        with open("temp_audio.mp3", "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            return f'<audio autoplay="true" src="data:audio/mp3;base64,{b64}">'
    except:
        return ""

def search_file(name, category):
    """Tìm kiếm file video hoặc ảnh dựa trên tên và chủ đề"""
    name_clean = unidecode(name).lower().strip()
    folders = ["video_train", "anh_train", "đồ dùng học tập", "động vật", "gia đình", "giao thông", "trái cây"]
    
    if category != "Tất cả":
        folders = [category]

    for folder in folders:
        if os.path.exists(folder):
            for file in os.listdir(folder):
                file_no_ext = unidecode(os.path.splitext(file)[0]).lower().strip()
                if name_clean == file_no_ext:
                    return os.path.join(folder, file)
    return None

# --- GIAO DIỆN STREAMLIT ---
st.set_page_config(page_title="NGÔN NGỮ KÝ HIỆU AI", layout="wide")
st.title("🤟 Hệ Thống Ngôn Ngữ Ký Hiệu AI")

col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("📷 Camera Nhận Diện")
    run_cam = st.toggle("Bật Camera")
    FRAME_WINDOW = st.image([])

    if run_cam:
        cap = cv2.VideoCapture(0)
        while run_cam:
            ret, frame = cap.read()
            if not ret:
                st.error("Không thể truy cập Camera.")
                break
            
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb_frame)

            # Vẽ kết quả nhận diện tay
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(
                        rgb_frame, 
                        hand_landmarks, 
                        mp_hands.HAND_CONNECTIONS
                    )
            
            FRAME_WINDOW.image(rgb_frame)
        cap.release()

with col_right:
    st.subheader("🔍 Tra cứu")
    search_query = st.text_input("Nhập chữ cái hoặc từ khóa:")
    category_option = st.selectbox("Chủ đề:", 
        ["Tất cả", "đồ dùng học tập", "động vật", "gia đình", "giao thông", "trái cây"])
    
    if st.button("Tìm kiếm"):
        if search_query:
            result_path = search_file(search_query, category_option)
            if result_path:
                st.success(f"Kết quả cho: {search_query}")
                if result_path.lower().endswith(('.mp4', '.avi', '.mkv')):
                    st.video(result_path)
                else:
                    st.image(result_path)
                # Phát âm thanh
                st.components.v1.html(get_audio_html(search_query), height=0)
            else:
                st.error("Không tìm thấy dữ liệu.")
