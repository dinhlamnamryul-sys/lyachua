import streamlit as st
import cv2
import mediapipe as mp
import av
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

# --- CLASS XỬ LÝ VIDEO VỚI AI MEDIAPIPE ---
class HandDetectorProcessor(VideoTransformerBase):
    def __init__(self):
        # Khởi tạo MediaPipe Hands
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils

    def transform(self, frame):
        # Nhận diện khung hình từ webcam
        img = frame.to_ndarray(format="bgr24")
        
        # Lật ảnh để người dùng dễ quan sát (hiệu ứng gương)
        img = cv2.flip(img, 1)
        
        # Chuyển màu sang RGB để MediaPipe xử lý
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = self.hands.process(img_rgb)

        # Kiểm tra nếu phát hiện bàn tay
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Vẽ các điểm nối và khớp xương tay
                self.mp_drawing.draw_landmarks(
                    img, 
                    hand_landmarks, 
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=4),
                    self.mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=2),
                )
            
            # Ghi chữ thông báo lên màn hình video
            cv2.putText(img, "DANG QUET TAY...", (20, 50), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        else:
            cv2.putText(img, "MOI GIO TAY LEN", (20, 50), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        return img

# --- GIAO DIỆN STREAMLIT ---
st.title("👐 Hệ thống Ngôn ngữ Ký hiệu AI")

tab1, tab2 = st.tabs(["📚 Thư viện học tập", "📷 Nhận diện AI"])

# TAB 1: THƯ VIỆN TRA CỨU
with tab1:
    col_search, col_display = st.columns([1, 2])
    
    with col_search:
        st.subheader("Tìm kiếm ký hiệu")
        search_query = st.text_input("Nhập tên ký hiệu (vd: Quả táo):")
        cat_filter = st.selectbox("Danh mục:", categories)
        btn = st.button("Tra cứu")

    with col_display:
        if btn or search_query:
            # Lọc dữ liệu dựa trên tìm kiếm
            results = [i for i in mock_library if search_query.lower() in i['name'].lower()]
            if results:
                res = results[0]
                st.success(f"Kết quả: {res['name']}")
                if res['type'] == 'video':
                    st.video(res['url'])
                else:
                    st.image(res['url'], use_container_width=True)
            else:
                st.error("Không tìm thấy ký hiệu này trong thư viện.")
        else:
            st.info("Vui lòng nhập tên ký hiệu để xem hình ảnh/video hướng dẫn.")

# TAB 2: CAMERA NHẬN DIỆN THỜI GIAN THỰC
with tab2:
    st.subheader("Nhận diện cử chỉ AI")
    st.write("Hãy nhấn **Start** và cho phép truy cập Camera. Hệ thống sẽ tự động quét các điểm đốt ngón tay của bạn.")
    
    # Sử dụng WebRTC để xử lý video mượt mà trên trình duyệt
    webrtc_streamer(
        key="hand-detection-sign-language",
        mode=WebRtcMode.SENDRECV,
        video_processor_factory=HandDetectorProcessor,
        media_stream_constraints={"video": True, "audio": False},
        async_processing=True,
    )

st.markdown("---")
st.caption("Ứng dụng được xây dựng bằng Python, Streamlit và MediaPipe AI.")
