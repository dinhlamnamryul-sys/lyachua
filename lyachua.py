import streamlit as st
import cv2
import mediapipe as mp
import av
import numpy as np
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase, WebRtcMode

# --- CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="Hệ thống NNKH AI",
    page_icon="👐",
    layout="wide"
)

# --- DỮ LIỆU GIẢ LẬP ---
mock_library = [
    {"id": 1, "name": "Xin chào", "category": "gia đình", "type": "video", "url": "https://www.w3schools.com/html/mov_bbb.mp4"},
    {"id": 2, "name": "Quả táo", "category": "trái cây", "type": "image", "url": "https://images.unsplash.com/photo-1560806887-1e4cd0b6bcd6?w=400"},
    {"id": 3, "name": "Bút chì", "category": "đồ dùng học tập", "type": "image", "url": "https://images.unsplash.com/photo-1512036667332-2323862660f9?w=400"},
    {"id": 4, "name": "Con mèo", "category": "động vật", "type": "video", "url": "https://www.w3schools.com/html/movie.mp4"},
    {"id": 5, "name": "Ô tô", "category": "giao thông", "type": "image", "url": "https://images.unsplash.com/photo-1494976388531-d1058494cdd8?w=400"},
]

categories = ["Tất cả", "Gia đình", "Trái cây", "Đồ dùng học tập", "Động vật", "Giao thông"]

# --- CLASS XỬ LÝ VIDEO AI (MEDIAPIPE) ---
class HandDetectorProcessor(VideoTransformerBase):
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils

    def transform(self, frame):
        img = frame.to_ndarray(format="bgr24")
        img = cv2.flip(img, 1)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = self.hands.process(img_rgb)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks(
                    img, 
                    hand_landmarks, 
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=4),
                    self.mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=2),
                )
            cv2.putText(img, "AI DANG QUET...", (30, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        else:
             cv2.putText(img, "HAY GIO TAY LEN...", (30, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        return img

# --- GIAO DIỆN CHÍNH ---
st.title("👐 Hệ thống Ngôn ngữ Ký hiệu AI")

tab1, tab2 = st.tabs(["📚 Thư viện học tập", "📷 Nhận diện AI"])

# TAB 1: THƯ VIỆN
with tab1:
    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("Tra cứu")
        search_term = st.text_input("Nhập từ khóa:")
        selected_cat = st.selectbox("Chọn danh mục:", categories)
        search_btn = st.button("Tìm kiếm")

    with col2:
        if search_btn or search_term:
            filtered = [i for i in mock_library if search_term.lower() in i['name'].lower()]
            if filtered:
                item = filtered[0]
                st.info(f"Đang hiển thị: {item['name']}")
                if item['type'] == 'video':
                    st.video(item['url'])
                else:
                    st.image(item['url'])
            else:
                st.error("Không tìm thấy kết quả.")
        else:
            st.write("Vui lòng nhập từ khóa để xem hướng dẫn ký hiệu.")

# TAB 2: NHẬN DIỆN
with tab2:
    st.subheader("Nhận diện tay thời gian thực")
    st.write("Nhấn Start để bắt đầu. Hệ thống sẽ sử dụng AI MediaPipe để quét các khớp ngón tay của bạn.")
    
    webrtc_streamer(
        key="hand-detection-app",
        mode=WebRtcMode.SENDRECV,
        video_processor_factory=HandDetectorProcessor,
        media_stream_constraints={"video": True, "audio": False},
        async_processing=True,
    )

st.markdown("---")
st.caption("Ứng dụng chạy trên nền tảng Streamlit & MediaPipe")
