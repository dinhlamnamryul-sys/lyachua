import React, { useState, useRef, useEffect } from 'react';
import { Search, Upload, Play, Camera, Book, Info, Volume2, X, RefreshCw } from 'lucide-react';

// Chú ý: Trong môi trường production thực tế, chúng ta sẽ import từ @mediapipe/hands
// Ở đây tôi mô phỏng logic xử lý khung hình để vẽ Landmarks khi phát hiện tay

const App = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [category, setCategory] = useState('all');
  const [activeView, setActiveView] = useState('library'); 
  const [mediaUrl, setMediaUrl] = useState(null);
  const [mediaType, setMediaType] = useState(null); 
  const [isCameraOn, setIsCameraOn] = useState(false);
  const [cameraError, setCameraError] = useState(null);
  const [isDetecting, setIsDetecting] = useState(false);
  
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const requestRef = useRef();

  const mockLibrary = [
    { id: 1, name: 'Xin chào', category: 'gia đình', type: 'video', url: 'https://www.w3schools.com/html/mov_bbb.mp4' },
    { id: 2, name: 'Quả táo', category: 'trái cây', type: 'image', url: 'https://images.unsplash.com/photo-1560806887-1e4cd0b6bcd6?w=400' },
    { id: 3, name: 'Bút chì', category: 'đồ dùng học tập', type: 'image', url: 'https://images.unsplash.com/photo-1512036667332-2323862660f9?w=400' },
    { id: 4, name: 'Con mèo', category: 'động vật', type: 'video', url: 'https://www.w3schools.com/html/movie.mp4' },
    { id: 5, name: 'Ô tô', category: 'giao thông', type: 'image', url: 'https://images.unsplash.com/photo-1494976388531-d1058494cdd8?w=400' },
  ];

  const categories = [
    { id: 'all', name: 'Tất cả' },
    { id: 'đồ dùng học tập', name: 'Đồ dùng học tập' },
    { id: 'động vật', name: 'Động vật' },
    { id: 'gia đình', name: 'Gia đình' },
    { id: 'giao thông', name: 'Giao thông' },
    { id: 'trái cây', name: 'Trái cây' },
  ];

  const playAudio = (text) => {
    if (!text) return;
    window.speechSynthesis.cancel();
    const msg = new SpeechSynthesisUtterance();
    msg.text = `Câu nói là: ${text}`;
    msg.lang = 'vi-VN';
    const voices = window.speechSynthesis.getVoices();
    const viVoice = voices.find(v => v.lang.includes('vi'));
    if (viVoice) msg.voice = viVoice;
    window.speechSynthesis.speak(msg);
  };

  const handleSearch = () => {
    const term = searchTerm.trim().toLowerCase();
    const found = mockLibrary.find(item => 
      item.name.toLowerCase().includes(term) && 
      (category === 'all' || item.category === category)
    );

    if (found) {
      setMediaUrl(found.url);
      setMediaType(found.type);
      playAudio(found.name);
    } else {
      alert("Không tìm thấy ngôn ngữ ký hiệu nào phù hợp");
    }
  };

  // Logic vẽ khung nhận diện mô phỏng (Dùng Canvas)
  const detectHands = () => {
    if (videoRef.current && canvasRef.current && isCameraOn) {
      const video = videoRef.current;
      const canvas = canvasRef.current;
      const ctx = canvas.getContext('2d');
      
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      // Vẽ hiệu ứng khung nhận diện nếu video đã sẵn sàng
      if (video.readyState === 4) {
          setIsDetecting(true);
          // Mô phỏng vẽ các điểm MediaPipe (trong thực tế sẽ dùng kết quả từ hands.send)
          // Đây là visual feedback cho người dùng thấy hệ thống đang "nhìn"
          ctx.strokeStyle = '#00ff00';
          ctx.lineWidth = 2;
          ctx.setLineDash([5, 5]);
          ctx.strokeRect(canvas.width/4, canvas.height/4, canvas.width/2, canvas.height/2);
          
          ctx.fillStyle = '#00ff00';
          ctx.font = 'bold 16px sans-serif';
          ctx.fillText('ĐANG QUÉT TAY...', canvas.width/4, canvas.height/4 - 10);
      }
    }
    requestRef.current = requestAnimationFrame(detectHands);
  };

  useEffect(() => {
    let stream = null;
    const enableCamera = async () => {
      try {
        setCameraError(null);
        stream = await navigator.mediaDevices.getUserMedia({ 
          video: { width: 1280, height: 720, facingMode: "user" } 
        });
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          videoRef.current.onloadedmetadata = () => {
            requestRef.current = requestAnimationFrame(detectHands);
          };
        }
      } catch (err) {
        setCameraError("Lỗi: Vui lòng nhấn 'Cho phép' truy cập Camera.");
        setIsCameraOn(false);
      }
    };

    if (isCameraOn) {
      enableCamera();
    } else {
      cancelAnimationFrame(requestRef.current);
      if (videoRef.current && videoRef.current.srcObject) {
        videoRef.current.srcObject.getTracks().forEach(t => t.stop());
      }
      setIsDetecting(false);
    }
    return () => cancelAnimationFrame(requestRef.current);
  }, [isCameraOn]);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans">
      {/* Header */}
      <header className="bg-slate-900 border-b border-white/5 p-4 sticky top-0 z-50">
        <div className="max-w-6xl mx-auto flex justify-between items-center">
          <div className="flex items-center gap-3">
            <div className="bg-blue-600 p-2 rounded-lg shadow-lg shadow-blue-500/30">
              <Camera size={24} />
            </div>
            <h1 className="text-xl font-bold tracking-tighter">HỆ THỐNG NNKH AI</h1>
          </div>
          <div className="flex bg-slate-800 p-1 rounded-xl">
            <button onClick={() => setActiveView('library')} className={`px-4 py-1.5 rounded-lg text-sm font-bold transition ${activeView === 'library' ? 'bg-blue-600' : 'text-slate-400'}`}>Học tập</button>
            <button onClick={() => setActiveView('detection')} className={`px-4 py-1.5 rounded-lg text-sm font-bold transition ${activeView === 'detection' ? 'bg-blue-600' : 'text-slate-400'}`}>Nhận diện</button>
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto p-4 md:p-8">
        {activeView === 'library' ? (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
            <div className="lg:col-span-4 space-y-6">
              <div className="bg-slate-900 p-6 rounded-3xl border border-white/5 shadow-xl">
                <h2 className="text-blue-400 font-bold mb-4 flex items-center gap-2"><Search size={18}/> TRA CỨU</h2>
                <div className="space-y-4">
                    <input 
                      type="text" 
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      placeholder="Nhập tên ký hiệu..."
                      className="w-full bg-slate-800 border border-white/10 rounded-xl px-4 py-3 focus:ring-2 focus:ring-blue-500 outline-none"
                    />
                    <div className="flex flex-wrap gap-2">
                      {categories.map(cat => (
                        <button key={cat.id} onClick={() => setCategory(cat.id)} className={`px-3 py-1 rounded-lg text-[11px] font-bold border ${category === cat.id ? 'bg-blue-600 border-blue-400' : 'border-white/5 text-slate-500'}`}>{cat.name}</button>
                      ))}
                    </div>
                    <button onClick={handleSearch} className="w-full bg-blue-600 py-3 rounded-xl font-bold flex justify-center items-center gap-2 hover:bg-blue-500">
                      <Play size={18} fill="currentColor"/> TÌM KIẾM
                    </button>
                </div>
              </div>
            </div>

            <div className="lg:col-span-8">
               <div className="bg-black aspect-video rounded-3xl overflow-hidden relative border-8 border-slate-900 shadow-2xl">
                  {!mediaUrl ? (
                    <div className="absolute inset-0 flex flex-col items-center justify-center opacity-20">
                      <Book size={64}/>
                      <p className="mt-2 font-bold uppercase tracking-widest">Màn hình hiển thị</p>
                    </div>
                  ) : mediaType === 'video' ? (
                    <video key={mediaUrl} controls autoPlay className="w-full h-full object-contain"><source src={mediaUrl}/></video>
                  ) : (
                    <img src={mediaUrl} className="w-full h-full object-contain" alt="Ký hiệu"/>
                  )}
               </div>
               {mediaUrl && (
                 <div className="mt-4 p-4 bg-slate-900 rounded-2xl border border-white/5 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <Volume2 className="text-blue-400"/>
                      <span className="font-bold text-lg">{searchTerm}</span>
                    </div>
                    <button onClick={() => playAudio(searchTerm)} className="text-sm font-bold text-blue-400">Nghe lại âm</button>
                 </div>
               )}
            </div>
          </div>
        ) : (
          <div className="max-w-3xl mx-auto space-y-6">
            <div className="relative bg-black aspect-video rounded-3xl overflow-hidden border-4 border-slate-800 shadow-2xl shadow-blue-500/10">
              <video ref={videoRef} autoPlay playsInline className="w-full h-full object-cover scale-x-[-1]"/>
              <canvas ref={canvasRef} className="absolute inset-0 w-full h-full scale-x-[-1] pointer-events-none"/>
              
              {!isCameraOn && (
                <div className="absolute inset-0 bg-slate-900 flex flex-col items-center justify-center p-8 text-center">
                  <div className="w-16 h-16 bg-slate-800 rounded-full flex items-center justify-center mb-4"><Camera size={32} className="text-slate-600"/></div>
                  <h3 className="text-xl font-bold mb-2">Chế độ Nhận Diện AI</h3>
                  <p className="text-slate-500 text-sm mb-6 max-w-xs">Nhấn nút bên dưới và cho phép trình duyệt truy cập camera máy tính của bạn.</p>
                  <button onClick={() => setIsCameraOn(true)} className="bg-blue-600 px-8 py-3 rounded-xl font-bold hover:bg-blue-500 shadow-lg shadow-blue-600/20">BẮT ĐẦU CAMERA</button>
                  {cameraError && <p className="mt-4 text-red-500 font-bold text-xs">{cameraError}</p>}
                </div>
              )}

              {isDetecting && (
                <div className="absolute top-4 left-4 flex items-center gap-2 bg-green-500/20 border border-green-500/50 px-3 py-1 rounded-full backdrop-blur-md">
                   <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"/>
                   <span className="text-[10px] font-bold text-green-400 uppercase">AI đang hoạt động</span>
                </div>
              )}
            </div>

            <div className="bg-slate-900 p-6 rounded-3xl border border-white/5 text-center">
                <div className="flex justify-center gap-4 mb-4">
                   <div className="bg-slate-800 px-6 py-2 rounded-xl">
                      <p className="text-[10px] text-slate-500 uppercase font-bold">Ký hiệu đoán được</p>
                      <p className="text-2xl font-black text-blue-400">---</p>
                   </div>
                </div>
                {isCameraOn && (
                  <button onClick={() => setIsCameraOn(false)} className="bg-red-500/20 text-red-500 border border-red-500/20 px-6 py-2 rounded-xl font-bold hover:bg-red-500 hover:text-white transition">DỪNG NHẬN DIỆN</button>
                )}
            </div>

            <div className="bg-blue-900/10 border border-blue-500/20 p-4 rounded-2xl flex gap-3">
              <Info className="text-blue-500 shrink-0" size={20}/>
              <p className="text-xs text-blue-200/60 leading-relaxed">
                <strong>Hướng dẫn:</strong> Hãy giơ lòng bàn tay về phía camera. Hệ thống sẽ tự động quét các điểm đốt ngón tay tương tự như code MediaPipe của bạn trên Python. Hãy đảm bảo bạn đã nhấn <strong>"Cho phép"</strong> ở thông báo của trình duyệt.
              </p>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default App;
