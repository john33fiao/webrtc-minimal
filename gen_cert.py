# gen_cert.py
import datetime
import ipaddress
import socket

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import datetime
import ipaddress
import socket

def get_local_ip():
    """로컬 PC의 IP 주소를 자동으로 가져옵니다."""
    try:
        # 외부 연결을 시도하여 로컬 IP를 알아냄 (실제 연결은 하지 않음)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        # 네트워크 연결이 없는 경우 기본값 반환
        return "127.0.0.1"

def generate_self_signed_cert():
    # 로컬 IP 주소 자동 감지
    local_ip = get_local_ip()
    print(f"🔍 감지된 로컬 IP: {local_ip}")

    # 1. 키 생성
    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    # 2. 서버 인증서 키/인증서 생성 (루트 CA로 서명)
    server_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    server_subject = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, u"KR"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"Seoul"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"My Local Network"),
        x509.NameAttribute(NameOID.COMMON_NAME, local_ip),
    ])

    # 3. 인증서 생성 (유효기간 365일)
    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.datetime.utcnow()
    ).not_valid_after(
        datetime.datetime.utcnow() + datetime.timedelta(days=365)
    ).add_extension(
        x509.SubjectAlternativeName([
            x509.DNSName(u"localhost"),
            x509.IPAddress(ipaddress.IPv4Address(local_ip)),
            x509.IPAddress(ipaddress.IPv6Address(u"::1")),
        ]),
        critical=False,
    ).sign(key, hashes.SHA256())

    # 4. 파일로 저장
    with open("key.pem", "wb") as f:
        f.write(
            server_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption(),
            )
        )

    with open("cert.pem", "wb") as f:
        f.write(server_cert.public_bytes(serialization.Encoding.PEM))

    with open("rootCA.pem", "wb") as f:
        f.write(ca_cert.public_bytes(serialization.Encoding.PEM))

    print("✅ 인증서 생성 완료: cert.pem, key.pem, rootCA.pem")
    print("ℹ️  루트 인증서(rootCA.pem)를 OS/디바이스에 신뢰하도록 추가하면 ‘Certificate error (-202)’와 같은 경고를 피할 수 있습니다.")


if __name__ == "__main__":
    generate_certificates()
