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
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- DỮ LIỆU GIẢ LẬP (MOCK DATA) ---
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
        # Khởi tạo MediaPipe Hands
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils

    def transform(self, frame):
        # Chuyển đổi khung hình từ WebRTC sang định dạng OpenCV
        img = frame.to_ndarray(format="bgr24")
        
        # Lật ngược ảnh cho giống gương
        img = cv2.flip(img, 1)
        
        # Chuyển sang RGB để MediaPipe xử lý
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = self.hands.process(img_rgb)

        # Vẽ Landmarks nếu phát hiện tay
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Vẽ khung xương tay
                self.mp_drawing.draw_landmarks(
                    img, 
                    hand_landmarks, 
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=4),
                    self.mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=2),
                )
                
            # Hiển thị thông báo trạng thái lên video
            cv2.putText(img, "AI DANG QUET...", (30, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.rectangle(img, (20, 20), (280, 70), (0, 255, 0), 2)
        else:
             cv2.putText(img, "HAY GIO TAY LEN...", (30, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        return img

# --- GIAO DIỆN CHÍNH (SIDEBAR) ---
st.sidebar.title("👐 Hệ thống NNKH")
active_view = st.sidebar.radio("Chọn chức năng:", ["📚 Thư viện học tập", "📷 Nhận diện AI"])

st.sidebar.info("Phiên bản Streamlit Python - Tích hợp MediaPipe thật.")

# --- VIEW 1: THƯ VIỆN HỌC TẬP ---
if active_view == "📚 Thư viện học tập":
    st.title("📚 Tra cứu Ngôn ngữ ký hiệu")
    
    # Khu vực tìm kiếm
    col1, col2 = st.columns([2, 1])
    with col1:
        search_term = st.text_input("🔍 Nhập tên ký hiệu:", placeholder="Ví dụ: Xin chào, Quả táo...")
    with col2:
        selected_cat = st.selectbox("📂 Danh mục:", categories)

    # Logic lọc dữ liệu
    filtered_items = []
    for item in mock_library:
        matches_search = search_term.lower() in item['name'].lower()
        matches_cat = selected_cat == "Tất cả" or item['category'].lower() == selected_cat.lower()
        
        if matches_search and matches_cat:
            filtered_items.append(item)

    st.markdown("---")

    # Hiển thị kết quả
    if search_term: # Chỉ hiện khi người dùng tìm kiếm hoặc chọn
        if filtered_items:
            item = filtered_items[0] # Lấy kết quả đầu tiên tìm thấy
            
            c1, c2 = st.columns([2, 1])
            with c1:
                st.subheader(f"Kết quả: {item['name']}")
                
                if item['type'] == 'video':
                    st.video(item['url'])
                else:
                    st.image(item['url'], use_container_width=True)
            
            with c2:
                st.write(f"**Danh mục:** {item['category']}")
                st.info(f"🔊 Đang phát âm thanh: '{item['name']}'")
                # Trong Python Streamlit, TTS phức tạp hơn, ta dùng thông báo giả lập
                st.success("Mô phỏng: Âm thanh đã được phát.")
        else:
            st.warning("Không tìm thấy kết quả nào phù hợp.")
    else:
        st.info("Vui lòng nhập từ khóa để tìm kiếm.")
        # Hiển thị lưới gợi ý
        st.subheader("Gợi ý phổ biến:")
        cols = st.columns(3)
        for idx, item in enumerate(mock_library[:3]):
            with cols[idx]:
                if item['type'] == 'image':
                    st.image(item['url'], caption=item['name'], use_container_width=True)
                else:
                    st.video(item['url'])
                    st.caption(item['name'])

# --- VIEW 2: NHẬN DIỆN AI ---
elif active_view == "📷 Nhận diện AI":
    st.title("📷 Camera Nhận diện (Real-time)")
    
    col_cam, col_info = st.columns([3, 1])
    
    with col_cam:
        st.write("Bật camera để hệ thống bắt đầu quét tay:")
        
        # Component WebRTC thay thế cho video tag của HTML5
        ctx = webrtc_streamer(
            key="hand-detection",
            mode=WebRtcMode.SENDRECV,
            video_processor_factory=HandDetectorProcessor,
            media_stream_constraints={"video": True, "audio": False},
            async_processing=True,
        )

    with col_info:
        st.markdown("### Trạng thái")
        if ctx.state.playing:
            st.success("Camera đang bật")
            st.info("AI đang phân tích khung hình...")
        else:
            st.warning("Camera đang tắt")
            
        st.markdown("---")
        st.metric(label="Dự đoán hiện tại", value="---")
        
        st.warning(
            """
            **Hướng dẫn:**
            1. Nhấn nút "START" bên dưới camera.
            2. Cho phép trình duyệt truy cập Webcam.
            3. Giơ tay lên trước camera để thấy khung xương tay được vẽ.
            """
        )

# Footer
st.markdown("---")
st.markdown("<center>Phát triển với ❤️ bằng Streamlit & MediaPipe</center>", unsafe_allow_html=True)
