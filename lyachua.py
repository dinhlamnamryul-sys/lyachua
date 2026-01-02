import streamlit as st
import cv2
import mediapipe as mp
import numpy as np
import os
from PIL import Image
from unidecode import unidecode
from gtts import gTTS
import base64

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="NGÔN NGỮ KÝ HIỆU AI", layout="wide")
st.title("🤟 Hệ Thống Học Ngôn Ngữ Ký Hiệu AI")

# --- KHỞI TẠO MEDIAPIPE ---
mp_hands = mp.solutions.hands [cite: 14]
hands = mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5) [cite: 15]
mp_drawing = mp.solutions.drawing_utils [cite: 24]

# --- HÀM HỖ TRỢ ---
def get_audio_html(text, lang='vi'):
    """Tạo HTML để tự động phát âm thanh gTTS trên trình duyệt"""
    tts = gTTS(text=text, lang=lang)
    tts.save("temp_audio.mp3")
    with open("temp_audio.mp3", "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        return f'<audio autoplay="true" src="data:audio/mp3;base64,{b64}">'

def process_frame(frame):
    """Xử lý khung hình để vẽ landmarks"""
    image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) [cite: 73]
    results = hands.process(image_rgb) [cite: 76]
    
    if results.multi_hand_landmarks: [cite: 89]
        for hand_landmarks in results.multi_hand_landmarks: [cite: 90]
            mp_drawing.draw_landmarks(
                frame, 
                hand_landmarks, 
                mp_hands.HAND_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2, circle_radius=2), [cite: 27]
                mp_drawing.DrawingSpec(color=(200, 0, 0), thickness=2, circle_radius=2) [cite: 28]
            )
    return frame

# --- GIAO DIỆN SIDEBAR (TÌM KIẾM) ---
st.sidebar.header("🔍 Tìm kiếm ký hiệu")
search_query = st.sidebar.text_input("Nhập câu nói hoặc chữ cái:") [cite: 165, 167]
chude_option = st.sidebar.selectbox("Chủ đề:", 
    ["Tất cả", "đồ dùng học tập", "động vật", "gia đình", "giao thông", "trái cây"]) [cite: 178, 180, 181, 182, 183, 184]

if st.sidebar.button("Tìm kiếm"): [cite: 169]
    found = False
    name_clean = unidecode(search_query).lower().strip() [cite: 31]
    
    # Logic quét thư mục từ mã gốc [cite: 33, 35, 47]
    folders = ["video_train", "anh_train", "đồ dùng học tập", "động vật", "gia đình", "giao thông", "trái cây"]
    if chude_option != "Tất cả":
        folders = [chude_option]

    for folder in folders:
        if os.path.exists(folder):
            for file in os.listdir(folder):
                if unidecode(os.path.splitext(file)[0]).lower() == name_clean:
                    file_path = os.path.join(folder, file) [cite: 53]
                    st.write(f"Kết quả cho: **{search_query}**")
                    
                    if file.lower().endswith(('.mp4', '.avi', '.mkv')): [cite: 54]
                        st.video(file_path) [cite: 55]
                    else:
                        st.image(file_path) [cite: 57]
                    
                    # Phát âm thanh thông báo
                    st.components.v1.html(get_audio_html(f"Kết quả của {search_query}"), height=0)
                    found = True
                    break
    if not found:
        st.sidebar.error("Không tìm thấy ngôn ngữ ký hiệu phù hợp") [cite: 61]

# --- GIAO DIỆN CHÍNH (NHẬN DIỆN CAMERA) ---
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📷 Nhận diện trực tiếp")
    run_camera = st.checkbox("Bật Camera nhận diện") [cite: 173]
    FRAME_WINDOW = st.image([])

    if run_camera:
        cap = cv2.VideoCapture(0) [cite: 64]
        while run_camera:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame = cv2.flip(frame, 1)
            frame = process_frame(frame)
            frame_display = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            FRAME_WINDOW.image(frame_display)
        cap.release()
    else:
        st.info("Nhấn dấu tích ở trên để bắt đầu nhận diện tay qua Camera.")

with col2:
    st.subheader("💡 Hướng dẫn & Ghi chú")
    st.markdown("""
    - **Ă, Â, Ê, Ô...**: Kết hợp chữ cái gốc và vẽ dấu trong khung hình.
    - **Phân biệt Số/Chữ**: Hệ thống sẽ dựa vào thời gian giữ tay (Hold time) hoặc chế độ chọn.
    - **Giọng nói**: Bạn có thể dùng biểu tượng micro trên bàn phím điện thoại/máy tính để nhập vào ô tìm kiếm.
    """)
    
    # Upload video để phân tích [cite: 149, 150]
    uploaded_file = st.file_uploader("Hoặc tải lên video để phân tích", type=['mp4', 'avi', 'mkv'])
    if uploaded_file is not None:
        st.video(uploaded_file)
        st.success(f"Đã tải lên: {uploaded_file.name}")
