import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from gtts import gTTS
import cv2
import mediapipe as mp
from unidecode import unidecode
import time
import pygame
import subprocess

# 1. Khởi tạo Mediapipe
mp_pose = mp.solutions.pose [cite: 12]
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) [cite: 13]
mp_hands = mp.solutions.hands [cite: 14]
hands = mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5) [cite: 15]

# 2. Cấu hình style vẽ
drawing_utils = mp.solutions.drawing_utils [cite: 24]
pose_landmark_style = drawing_utils.DrawingSpec(color=(0, 255, 0), thickness=1, circle_radius=1) [cite: 25]
pose_connection_style = drawing_utils.DrawingSpec(color=(0, 200, 0), thickness=1, circle_radius=1) [cite: 26]
hand_landmark_style = drawing_utils.DrawingSpec(color=(255, 0, 0), thickness=1, circle_radius=1) [cite: 27]
hand_connection_style = drawing_utils.DrawingSpec(color=(200, 0, 0), thickness=1, circle_radius=1) [cite: 28]

def run_nhadientay():
    try:
        subprocess.run(['python', 'nhandientay.py'], check=True) [cite: 18]
        print("Chạy file nhadientay.py thành công.") [cite: 19]
    except Exception as e:
        messagebox.showerror("Lỗi", f"Lỗi khi chạy file nhadientay.py: {e}") [cite: 22]

def search_and_display():
    name = entry.get().strip() [cite: 30]
    name = unidecode(name).lower() [cite: 31]
    found = False
    folders_to_search = []
    
    current_topic = var_chude.get() [cite: 34]
    if current_topic == "all":
        folders_to_search = ["video_train", "anh_train", "đồ dùng học tập", "động vật", "gia đình", "giao thông", "trái cây"] [cite: 35]
    else:
        folders_to_search.append(current_topic) [cite: 37-46]

    for folder in folders_to_search:
        if os.path.exists(folder): [cite: 48]
            for file in os.listdir(folder): [cite: 49]
                file_name_without_ext = os.path.splitext(file)[0].strip() [cite: 50]
                file_name_without_ext = unidecode(file_name_without_ext).lower() [cite: 51]
                
                if name == file_name_without_ext: [cite: 52]
                    file_path = os.path.join(folder, file) [cite: 53]
                    if file.lower().endswith(('.mp4', '.avi', '.mkv')): [cite: 54]
                        play_video(file_path) [cite: 55]
                    elif file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')): [cite: 56]
                        display_image(file_path) [cite: 57]
                    found = True
                    break
    if not found:
        messagebox.showinfo("Thông báo", "Không tìm thấy ngôn ngữ ký hiệu nào phù hợp") [cite: 61]

def play_video(file_path):
    try:
        cap = cv2.VideoCapture(file_path) [cite: 64]
        while cap.isOpened():
            ret, frame = cap.read() [cite: 68]
            if not ret: break [cite: 69, 70]
            
            # Xử lý MediaPipe [cite: 71-76]
            frame_small = cv2.resize(frame, (320, 240)) [cite: 72]
            frame_rgb = cv2.cvtColor(frame_small, cv2.COLOR_BGR2RGB) [cite: 73]
            results_pose = pose.process(frame_rgb) [cite: 75]
            results_hands = hands.process(frame_rgb) [cite: 76]
            
            # Chuẩn bị hiển thị [cite: 78, 79]
            frame_display = cv2.resize(frame, (640, 480)) [cite: 78]
            frame_display_rgb = cv2.cvtColor(frame_display, cv2.COLOR_BGR2RGB) [cite: 79]
            
            # Vẽ Pose [cite: 81-88]
            if results_pose.pose_landmarks:
                mp.solutions.drawing_utils.draw_landmarks(
                    frame_display_rgb, results_pose.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                    landmark_drawing_spec=pose_landmark_style, connection_drawing_spec=pose_connection_style)
            
            # Vẽ Hands [cite: 89-97]
            if results_hands.multi_hand_landmarks:
                for hand_landmarks in results_hands.multi_hand_landmarks:
                    mp.solutions.drawing_utils.draw_landmarks(
                        frame_display_rgb, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                        landmark_drawing_spec=hand_landmark_style, connection_drawing_spec=hand_connection_style)
            
            # Cập nhật Canvas [cite: 101-105]
            img = Image.fromarray(frame_display_rgb)
            img_tk = ImageTk.PhotoImage(image=img)
            canvas.create_image(0, 0, anchor="nw", image=img_tk)
            canvas.image = img_tk
            canvas.update()
        cap.release() [cite: 106]
    except Exception as e:
        messagebox.showerror("Lỗi", f"Không thể phát video: {e}") [cite: 108]

def display_image(file_path):
    try:
        image = Image.open(file_path) [cite: 111]
        image = image.resize((640, 480), Image.Resampling.LANCZOS) [cite: 112]
        image_tk = ImageTk.PhotoImage(image) [cite: 113]
        canvas.create_image(0, 0, anchor="nw", image=image_tk) [cite: 114]
        canvas.image = image_tk [cite: 115]
        canvas.update() [cite: 116]
    except Exception as e:
        messagebox.showerror("Lỗi", f"Không thể hiển thị ảnh: {e}") [cite: 118]

def play_audio(file_name):
    file_path = "temp_audio.mp3" [cite: 120]
    if os.path.exists(file_path): [cite: 121]
        try: os.remove(file_path) [cite: 123]
        except: pass
    try:
        tts = gTTS(text=f"Câu nói là: {file_name}", lang='vi') [cite: 128]
        tts.save(file_path) [cite: 129]
        pygame.mixer.init() [cite: 134]
        pygame.mixer.music.load(file_path) [cite: 136]
        pygame.mixer.music.play() [cite: 137]
        while pygame.mixer.music.get_busy(): time.sleep(0.2) [cite: 138, 139]
    finally:
        pygame.mixer.quit() [cite: 147]

def play_predefined_video():
    video_file = filedialog.askopenfilename(filetypes=[("Video", "*.mp4;*.avi;*.mkv")]) [cite: 150]
    if video_file:
        name = os.path.splitext(os.path.basename(video_file))[0] [cite: 153]
        play_video(video_file) [cite: 154]
        play_audio(name) [cite: 155]

# 3. Giao diện Tkinter
root = tk.Tk() [cite: 158]
root.title("NGÔN NGỮ KÝ HIỆU AI") [cite: 159]
root.geometry("640x750") [cite: 160]

canvas = tk.Canvas(root, width=640, height=480, bg="black") [cite: 161]
canvas.pack() [cite: 162]

frame_search = tk.Frame(root) [cite: 163]
frame_search.pack(pady=10) [cite: 164]

tk.Label(frame_search, text="Nhập câu nói:").pack(side=tk.LEFT) [cite: 165, 166]
entry = tk.Entry(frame_search, width=30) [cite: 167]
entry.pack(side=tk.LEFT, padx=5) [cite: 168]

tk.Button(frame_search, text="Tìm kiếm", command=search_and_display).pack(side=tk.LEFT) [cite: 169, 170]
tk.Button(root, text="Lấy video có sẵn", command=play_predefined_video).pack(pady=5) [cite: 171, 172]
tk.Button(root, text="Chạy Nhận Diện Tay", command=run_nhadientay).pack(pady=5) [cite: 173, 174]

var_chude = tk.StringVar(value="all") [cite: 175]
chude_frame = tk.Frame(root) [cite: 176, 177]
chude_frame.pack()

topics = [("Tất cả", "all"), ("Học tập", "đồ dùng học tập"), ("Động vật", "động vật"), 
          ("Gia đình", "gia đình"), ("Giao thông", "giao thông"), ("Trái cây", "trái cây")]

for text, val in topics:
    tk.Radiobutton(chude_frame, text=text, variable=var_chude, value=val).pack(side=tk.LEFT) [cite: 178-189]

root.mainloop() [cite: 190]
