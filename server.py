# server.py
import os
from aiohttp import web
import socketio
import ssl  # [추가] SSL 모듈 임포트

# 환경변수에서 설정 로드 (기본값 제공)
PORT = int(os.environ.get('PORT', 3000))
SSL_CERT_PATH = os.environ.get('SSL_CERT_PATH', 'cert.pem')
SSL_KEY_PATH = os.environ.get('SSL_KEY_PATH', 'key.pem')

# 1. Socket.IO 서버 생성 (CORS 허용)
sio = socketio.AsyncServer(async_mode='aiohttp', cors_allowed_origins='*')
app = web.Application()
sio.attach(app)

# 2. 정적 파일 서빙
app.router.add_static('/public', './public')

async def index(request):
    # HTTPS 접속 시에도 동일하게 리다이렉트
    raise web.HTTPFound('/public/viewer.html')

app.router.add_get('/', index)

# ---------------------------------------------------------
# 3. Socket.IO 이벤트 처리
# ---------------------------------------------------------

@sio.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")
    # [유지] await 필수
    await sio.enter_room(sid, 'room1') 
    print(f"Client {sid} joined room1")

@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")
    # [유지] await 필수
    await sio.leave_room(sid, 'room1')

@sio.event
async def offer(sid, data):
    await sio.emit('offer', data, room='room1', skip_sid=sid)

@sio.event
async def answer(sid, data):
    await sio.emit('answer', data, room='room1', skip_sid=sid)

@sio.on('ice-candidate')
async def on_ice_candidate(sid, data):
    await sio.emit('ice-candidate', data, room='room1', skip_sid=sid)

@sio.on('request_start_camera')
async def on_request_start(sid):
    print(f"Request start camera from {sid}")
    await sio.emit('cmd_start_camera', room='room1', skip_sid=sid)

@sio.on('send_input_coordinates')
async def on_input_coords(sid, data):
    # print(f"Input received from {sid}: {data}")
    await sio.emit('cmd_input_coordinates', data, room='room1', skip_sid=sid)


@sio.on('annotation:point')
async def on_annotation_point(sid, data):
    """중앙에서 판서 좌표를 릴레이한다.

    현재는 별도의 RTCDataChannel을 사용하지 않고 Socket.IO 채널을 재사용한다.
    좌표는 정규화된 값(0~1)을 기대하며, 동일 룸의 다른 피어에게만 전달된다.
    """
    await sio.emit('annotation:point', data, room='room1', skip_sid=sid)

# ---------------------------------------------------------
# 4. 서버 실행 (HTTPS 설정 추가)
# ---------------------------------------------------------
if __name__ == '__main__':
    # SSL 컨텍스트 생성
    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    
    try:
        # [중요] 인증서 파일 로드 (환경변수 또는 기본값 사용)
        ssl_context.load_cert_chain(SSL_CERT_PATH, SSL_KEY_PATH)
        
        print(f"🔒 HTTPS Local Server running on https://0.0.0.0:{PORT}")
        print("⚠️  브라우저 접속 시 '고급 -> 안전하지 않음으로 이동'을 눌러주세요.")
        
        # ssl_context 추가하여 실행
        web.run_app(app, port=PORT, ssl_context=ssl_context)
        
    except FileNotFoundError:
        print(f"❌ [오류] 인증서 파일({SSL_CERT_PATH}, {SSL_KEY_PATH})을 찾을 수 없습니다.")
        print("   먼저 gen_cert.py를 실행하여 인증서를 생성해주세요.")