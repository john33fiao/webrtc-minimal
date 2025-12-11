# server.py
from aiohttp import web
import socketio

# 1. Socket.IO 서버 생성 (CORS 허용)
sio = socketio.AsyncServer(async_mode='aiohttp', cors_allowed_origins='*')
app = web.Application()
sio.attach(app)

# 2. 정적 파일(HTML) 서빙 설정
# 'public' 폴더에 있는 viewer.html, camera.html을 제공하기 위함
# 실행 위치에 public 폴더가 있어야 합니다.
app.router.add_static('/public', './public')

# 루트 접속 시 viewer.html로 리다이렉트 (편의상)
async def index(request):
    raise web.HTTPFound('/public/viewer.html')

app.router.add_get('/', index)

# ---------------------------------------------------------
# 3. Socket.IO 이벤트 처리 (Node.js 로직과 동일)
# ---------------------------------------------------------

@sio.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")
    # 단순화를 위해 모든 접속자를 'room1'에 입장시킴
    sio.enter_room(sid, 'room1')

@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")
    sio.leave_room(sid, 'room1')

# WebRTC Signaling (SDP, ICE Candidate 교환)
# skip_sid=sid : 보낸 사람에게는 다시 보내지 않음 (broadcast)

@sio.event
async def offer(sid, data):
    await sio.emit('offer', data, room='room1', skip_sid=sid)

@sio.event
async def answer(sid, data):
    await sio.emit('answer', data, room='room1', skip_sid=sid)

@sio.event
async def ice_candidate(sid, data):
    # 클라이언트에서 이벤트명을 'ice-candidate'로 보낼 경우를 대비해 함수명은 언더바 사용
    # 실제 이벤트명 매핑은 데코레이터로 가능하지만, python-socketio는
    # 함수명 'ice_candidate'를 이벤트 'ice_candidate'로 자동 매핑함.
    # 클라이언트 코드의 '-'를 '_'로 맞춰주거나 명시적 매핑이 필요함.
    # 여기서는 편의를 위해 클라이언트가 'ice_candidate'로 보낸다고 가정하거나
    # 아래와 같이 명시적으로 이벤트를 등록합니다.
    await sio.emit('ice-candidate', data, room='room1', skip_sid=sid)

# 이벤트명에 하이픈(-)이 있는 경우 별도 등록
@sio.on('ice-candidate')
async def on_ice_candidate(sid, data):
    await sio.emit('ice-candidate', data, room='room1', skip_sid=sid)

# 제어 명령: 촬영 시작 요청
@sio.on('request_start_camera')
async def on_request_start(sid):
    await sio.emit('cmd_start_camera', room='room1', skip_sid=sid)

# 입력 전송: 마우스 좌표
@sio.on('send_input_coordinates')
async def on_input_coords(sid, data):
    print(f"Input received from {sid}: {data}")
    await sio.emit('cmd_input_coordinates', data, room='room1', skip_sid=sid)

# ---------------------------------------------------------
# 4. 서버 실행
# ---------------------------------------------------------
if __name__ == '__main__':
    print("Python Signaling Server running on http://localhost:3000")
    web.run_app(app, port=3000)