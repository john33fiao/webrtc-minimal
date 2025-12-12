# WebRTC 1:1 영상 스트리밍 및 원격 제어

두 장치 간에 WebRTC를 사용하여 실시간으로 영상을 스트리밍하고, 한 쪽에서 다른 쪽을 원격으로 제어하는 기능을 구현한 프로젝트입니다.

## 현재 코드 상태 요약

- Python `aiohttp` + `python-socketio` 기반 HTTPS 서버로 동작하며, 기본 포트는 `3000`입니다.
- STUN 서버를 사용하지 않는 LAN 환경 전용 구성으로, ICE 후보는 Socket.IO를 통해 교환됩니다.
- 로컬 테스트용 `cert.pem`/`key.pem`이 필요하며 없을 경우 `gen_cert.py`로 생성해야 합니다.
- 카메라 권한이 없으면 캔버스 기반 더미 스트림을 생성해 뷰어로 전송합니다.
- Socket.IO 브라우저 클라이언트는 CDN 대신 `public/socket.io.min.js`를 직접 참조합니다.

## 판서 기능 진행 상황

### ✅ 구현 완료
- **양방향 판서 동기화**: 뷰어와 카메라 페이지 모두 영상 위에 캔버스 오버레이를 유지하며, 좌표는 0~1 범위로 정규화하여 송수신합니다.
- **Socket.IO 기반 좌표 전송**: 판서 좌표는 `annotation:point` 이벤트로 양방향 전달되며, 수신 시 캔버스에 즉시 렌더링합니다.
- **카메라 측 영상 합성**: 카메라 페이지에서 `<video>` + `<canvas>`를 합성 캔버스에 그린 뒤 `captureStream()`으로 WebRTC 스트림을 생성하여 송출합니다.
- **드래그 판서 지원**: 마우스/터치 드래그로 선을 그릴 수 있으며, `isStart`/`isEnd` 플래그로 스트로크 단위를 구분합니다.
- **10초 자동 만료**: 각 스트로크는 `STROKE_LIFETIME_MS`(10초) 후 자동으로 삭제되어 화면에서 사라집니다.
- **색상 구분**: 카메라 측은 민트색(`#5eead4`), 뷰어 측은 파란색(`#0000FF`)으로 고정되어 어느 쪽에서 그렸는지 구분됩니다.

### 🚧 미구현 (MVP 범위)
- 서버 측 판서가 카메라 측 영상 스트림에 재합성되지 않음 (오버레이로만 표시)
- Undo/Redo, 전체 지우기 기능
- 판서 로그 영구 저장

세부 남은 항목은 [TODO.md](./TODO.md)에 정리되어 있습니다.

## 기능

*   **WebRTC 기반 영상 스트리밍**: 카메라 클라이언트에서 뷰어 클라이언트로 영상을 실시간 전송합니다.
*   **HTTPS 서버**: WebRTC는 보안 연결(HTTPS)을 필요로 하므로, Python의 `aiohttp`와 `ssl` 모듈을 사용하여 자체 서명된 인증서로 HTTPS 서버를 구동합니다.
*   **Socket.IO 시그널링**: WebRTC 연결 설정을 위한 시그널링(Offer, Answer, ICE Candidate 교환)을 `socket.io`를 통해 처리합니다.
*   **원격 제어**:
    *   **촬영 시작 요청**: 뷰어에서 카메라 클라이언트에게 영상 촬영 및 전송을 시작하도록 요청할 수 있습니다.
    *   **좌표 전송**: 뷰어의 영상 화면을 클릭하면 해당 좌표가 카메라 클라이언트로 전송됩니다. (이 좌표를 활용한 추가 제어 가능)

## 전제 조건

*   Python 3.7+
*   pip

## 설정 및 설치

1.  **저장소 복제:**

    ```bash
    git clone https://github.com/john33fiao/webrtc-minimal.git
    cd webrtc-minimal
    ```

2.  **Python 가상 환경 생성 및 활성화 (권장):**

    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```

3.  **필요한 라이브러리 설치:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **SSL 인증서 생성:**

    WebRTC는 보안 연결(HTTPS)에서만 동작하므로, 로컬 테스트를 위한 자체 서명 인증서를 생성해야 합니다.

    ```bash
    python gen_cert.py
    ```

    이 명령을 실행하면 프로젝트 루트 디렉터리에 `cert.pem`과 `key.pem` 파일이 생성됩니다.

5.  **서버 실행:**

    ```bash
    python server.py
    ```

    서버가 정상적으로 실행되면 다음과 같은 메시지가 표시됩니다.
    ```
    🔒 HTTPS Local Server running on https://0.0.0.0:3000
    ⚠️  브라우저 접속 시 '고급 -> 안전하지 않음으로 이동'을 눌러주세요.
    ```

## 사용법

1.  **뷰어(Viewer) 접속:**

    *   PC의 웹 브라우저를 열고 `https://localhost:3000` 또는 `https://<PC의-내부-IP>:3000` 주소로 접속합니다.
    *   "안전하지 않음" 경고가 표시되면 **고급**을 클릭하고 **안전하지 않은 사이트로 이동**을 선택합니다.
    *   "Server (Video Receiver)" 페이지가 나타납니다.

2.  **카메라(Camera) 접속:**

    *   스마트폰이나 다른 PC의 웹 브라우저를 열고 `https://<서버-PC의-내부-IP>:3000/public/camera.html` 주소로 접속합니다.
        *   `<서버-PC의-내부-IP>`는 `ipconfig` (Windows) 또는 `ifconfig` (macOS/Linux) 명령어로 확인할 수 있습니다.
        *   두 장치는 동일한 네트워크(Wi-Fi)에 연결되어 있어야 합니다.
    *   마찬가지로 "안전하지 않음" 경고를 무시하고 접속합니다.
    *   "Client (Camera Sender)" 페이지가 나타나고 카메라 사용 권한을 요청하면 **허용**합니다.

3.  **스트리밍 시작:**

    *   뷰어 페이지에서 **촬영 시작 요청** 버튼을 클릭합니다.
    *   잠시 후, 카메라 클라이언트의 영상이 뷰어 페이지에 나타납니다.

4.  **원격 입력 테스트:**
    *   뷰어 페이지의 영상 화면을 클릭하면, 서버 로그와 브라우저 콘솔에 좌표가 출력되는 것을 확인할 수 있습니다.

## 파일 구조

```
.
├── .gitignore
├── AGENTS.md         # AI 에이전트용 작업 지침
├── gen_cert.py       # SSL 인증서(cert.pem, key.pem) 생성 스크립트
├── server.py         # aiohttp 기반의 웹 및 Socket.IO 시그널링 서버
├── requirements.txt  # 필요한 Python 패키지 목록
├── README.md         # 프로젝트 설명서
├── TODO.md           # 판서 기능 구현 체크리스트
└── public/
    ├── camera.html       # 영상 촬영 및 전송 클라이언트 페이지
    ├── viewer.html       # 영상 수신 및 원격 제어용 뷰어 페이지
    └── socket.io.min.js  # Socket.IO 클라이언트 라이브러리
```

## 주요 Socket.IO 이벤트

| 이벤트 | 방향 | 설명 |
|--------|------|------|
| `request_start_camera` | Viewer → Server → Camera | 촬영 시작 요청 |
| `cmd_start_camera` | Server → Camera | 촬영 시작 명령 |
| `offer` / `answer` | 양방향 | WebRTC SDP 교환 |
| `ice-candidate` | 양방향 | ICE 후보 교환 |
| `annotation:point` | 양방향 | 판서 좌표 릴레이 (`x`, `y`, `source`, `color`, `isStart`, `isEnd`) |

## 판서 기능 TODO (MVP)

판서 기능을 추가하기 위한 세부 TODO는 [TODO.md](./TODO.md)에서 확인할 수 있습니다. 근무자(송출)와 서버(관제) 웹앱에 필요한 레이아웃, 오버레이 UI, 판서 동기화 및 라이프사이클 관리 항목을 체크리스트로 정리했습니다.
