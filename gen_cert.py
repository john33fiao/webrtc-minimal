# gen_cert.py
import datetime
import ipaddress
import socket

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID

def _collect_ip_addresses():
    """로컬 IP 주소 목록(IPv4/IPv6)을 수집합니다."""

    ips = {ipaddress.ip_address("127.0.0.1")}
    try:
        for family, _, _, _, sockaddr in socket.getaddrinfo(socket.gethostname(), None):
            # sockaddr는 (ip, port, flowinfo, scope_id) 등 다양한 형식으로 반환될 수 있음
            raw_ip = sockaddr[0]
            try:
                ip_obj = ipaddress.ip_address(raw_ip)
            except ValueError:
                continue

            if family in (socket.AF_INET, socket.AF_INET6):
                ips.add(ip_obj)
    except socket.gaierror:
        # 네트워크 설정 문제로 IP를 찾지 못하더라도 loopback만 포함해 진행
        pass

    return sorted(ips, key=lambda ip: (ip.version, ip.compressed))


def generate_certificates():
    # 1. 루트 CA 키/인증서 생성 (신뢰 가능하도록 개별 파일로 제공)
    ca_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    ca_subject = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, u"KR"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"Seoul"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"WebRTC Local CA"),
        x509.NameAttribute(NameOID.COMMON_NAME, u"WebRTC Local Root"),
    ])

    ca_cert = (
        x509.CertificateBuilder()
        .subject_name(ca_subject)
        .issuer_name(ca_subject)
        .public_key(ca_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.utcnow())
        .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=365))
        .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
        .sign(ca_key, hashes.SHA256())
    )

    # 2. 서버 인증서 키/인증서 생성 (루트 CA로 서명)
    server_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    server_subject = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, u"KR"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"Seoul"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"My Local Network"),
        x509.NameAttribute(NameOID.COMMON_NAME, u"localhost"),
    ])

    alt_names = [x509.DNSName(u"localhost")]
    for ip in _collect_ip_addresses():
        alt_names.append(x509.IPAddress(ip))

    server_cert = (
        x509.CertificateBuilder()
        .subject_name(server_subject)
        .issuer_name(ca_cert.subject)
        .public_key(server_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.utcnow())
        .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=365))
        .add_extension(x509.SubjectAlternativeName(alt_names), critical=False)
        .add_extension(
            x509.ExtendedKeyUsage([ExtendedKeyUsageOID.SERVER_AUTH]),
            critical=False,
        )
        .add_extension(
            x509.BasicConstraints(ca=False, path_length=None),
            critical=True,
        )
        .sign(ca_key, hashes.SHA256())
    )

    # 3. 파일로 저장
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
