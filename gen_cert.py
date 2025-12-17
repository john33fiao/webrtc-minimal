from cryptography import x509
from cryptography.x509.oid import NameOID, ExtendedKeyUsageOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import datetime
import ipaddress
from pathlib import Path
import socket

ROOT_CA_CERT_PATH = Path("rootCA.pem")
ROOT_CA_KEY_PATH = Path("rootCA-key.pem")
SERVER_CERT_PATH = Path("cert.pem")
SERVER_KEY_PATH = Path("key.pem")


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


def load_or_create_root_ca():
    if ROOT_CA_CERT_PATH.exists() and ROOT_CA_KEY_PATH.exists():
        print("📄 기존 루트 CA를 재사용합니다.")
        ca_key = serialization.load_pem_private_key(
            ROOT_CA_KEY_PATH.read_bytes(), password=None
        )
        ca_cert = x509.load_pem_x509_certificate(ROOT_CA_CERT_PATH.read_bytes())
        return ca_key, ca_cert

    print("🆕 새 루트 CA를 생성합니다 (mkcert 스타일).")
    ca_key = rsa.generate_private_key(public_exponent=65537, key_size=4096)
    subject = x509.Name(
        [
            x509.NameAttribute(NameOID.COUNTRY_NAME, u"KR"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"Seoul"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"webrtc-minimal local CA"),
            x509.NameAttribute(NameOID.COMMON_NAME, u"webrtc-minimal.local CA"),
        ]
    )

    now = datetime.datetime.now(datetime.timezone.utc)

    ca_cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(subject)
        .public_key(ca_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - datetime.timedelta(minutes=5))
        .not_valid_after(now + datetime.timedelta(days=3650))
        .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
        .add_extension(
            x509.SubjectKeyIdentifier.from_public_key(ca_key.public_key()),
            critical=False,
        )
        .add_extension(
            x509.AuthorityKeyIdentifier.from_issuer_public_key(ca_key.public_key()),
            critical=False,
        )
        .sign(ca_key, hashes.SHA256())
    )

    ROOT_CA_KEY_PATH.write_bytes(
        ca_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )
    ROOT_CA_CERT_PATH.write_bytes(ca_cert.public_bytes(serialization.Encoding.PEM))
    print("✅ 루트 CA 생성 완료: rootCA.pem, rootCA-key.pem")
    return ca_key, ca_cert


def build_subject_alternative_names(local_ip: str):
    alt_names = [x509.DNSName(u"localhost")]
    candidates = {"127.0.0.1", "::1", local_ip}

    for candidate in candidates:
        try:
            alt_names.append(x509.IPAddress(ipaddress.ip_address(candidate)))
        except ValueError:
            continue

    unique_alt_names = []
    seen = set()
    for name in alt_names:
        key = (type(name), name.value)
        if key not in seen:
            seen.add(key)
            unique_alt_names.append(name)

    return x509.SubjectAlternativeName(unique_alt_names)


def generate_mkcert_style_cert():
    local_ip = get_local_ip()
    print(f"🔍 감지된 로컬 IP: {local_ip}")

    ca_key, ca_cert = load_or_create_root_ca()

    server_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = x509.Name(
        [
            x509.NameAttribute(NameOID.COUNTRY_NAME, u"KR"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"Seoul"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"webrtc-minimal dev server"),
            x509.NameAttribute(NameOID.COMMON_NAME, u"webrtc-minimal.local"),
        ]
    )

    alt_names = build_subject_alternative_names(local_ip)

    now = datetime.datetime.now(datetime.timezone.utc)

    server_cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(ca_cert.subject)
        .public_key(server_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - datetime.timedelta(minutes=5))
        .not_valid_after(now + datetime.timedelta(days=365))
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .add_extension(alt_names, critical=False)
        .add_extension(
            x509.ExtendedKeyUsage([ExtendedKeyUsageOID.SERVER_AUTH]), critical=False
        )
        .add_extension(
            x509.KeyUsage(
                digital_signature=True,
                key_encipherment=True,
                content_commitment=False,
                data_encipherment=False,
                key_agreement=True,
                key_cert_sign=False,
                crl_sign=False,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=False,
        )
        .sign(ca_key, hashes.SHA256())
    )

    SERVER_KEY_PATH.write_bytes(
        server_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )
    SERVER_CERT_PATH.write_bytes(server_cert.public_bytes(serialization.Encoding.PEM))

    print("✅ 인증서 생성 완료: cert.pem, key.pem (루트: rootCA.pem)")


if __name__ == "__main__":
    generate_mkcert_style_cert()
