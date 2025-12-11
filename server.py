# server.py
from aiohttp import web
import socketio

# 1. Socket.IO 서버 생성 (CORS 허용)
sio = socketio.AsyncServer(async_mode='aiohttp', cors_allowed_origins='*')
app = web.Application()
sio.attach(app)

# 2. 정적 파일 서빙
app.router.add_static('/public', './public')

async def index(request):
    raise web.HTTPFound('/public/viewer.html')

app.router.add_get('/', index)

# ---------------------------------------------------------
# 3. Socket.IO 이벤트 처리
# ---------------------------------------------------------

@sio.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")
    # [수정] await 추가 필수!
    await sio.enter_room(sid, 'room1') 
    print(f"Client {sid} joined room1")

@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")
    # [수정] await 추가 필수!
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
    # print(f"Input received from {sid}: {data}") # 로그 너무 많으면 주석 처리
    await sio.emit('cmd_input_coordinates', data, room='room1', skip_sid=sid)

# ---------------------------------------------------------
# 4. 서버 실행
# ---------------------------------------------------------
if __name__ == '__main__':
    print("Python Signaling Server running on http://localhost:3000")
    web.run_app(app, port=3000)