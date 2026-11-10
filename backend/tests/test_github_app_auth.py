import httpx
import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from app.auth.oauth import GitHubOAuth
from app.github.app_auth import GitHubAppAuth


def _rsa_keypair() -> tuple[str, str]:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode()
    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode()
    return private_pem, public_pem


def test_app_jwt_and_installation_token() -> None:
    private_pem, public_pem = _rsa_keypair()
    calls: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request.url.path)
        assert request.headers["Authorization"].startswith("Bearer ")
        if request.url.path.endswith("/access_tokens"):
            return httpx.Response(201, json={"token": "installation-token"})
        if request.url.path.endswith("/installation/repositories"):
            return httpx.Response(
                200,
                json={"repositories": [{"id": 1, "full_name": "duyendojhs/SE2026-T07"}]},
            )
        return httpx.Response(200, json={"id": 42, "account": {"login": "duyendojhs"}})

    app_auth = GitHubAppAuth(
        app_id=123,
        private_key=private_pem,
        base_url="https://api.github.com",
        transport=httpx.MockTransport(handler),
    )
    token = app_auth.app_jwt()
    decoded = jwt.decode(token, public_pem, algorithms=["RS256"], options={"verify_aud": False})
    assert decoded["iss"] == "123"

    assert app_auth.installation_token(42) == "installation-token"
    assert app_auth.installation(42)["id"] == 42
    assert app_auth.installation_repositories(42)[0]["id"] == 1
    assert calls[0] == "/app/installations/42/access_tokens"
    app_auth.close()


def test_oauth_authorize_and_exchange() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/login/oauth/access_token":
            return httpx.Response(200, json={"access_token": "user-token"})
        if request.url.path == "/user":
            assert request.headers["Authorization"] == "Bearer user-token"
            return httpx.Response(200, json={"id": 1, "login": "alice"})
        return httpx.Response(404)

    oauth = GitHubOAuth(
        client_id="client-id",
        client_secret="client-secret",
        oauth_url="https://github.com/login/oauth",
        api_url="https://api.github.com",
        transport=httpx.MockTransport(handler),
    )

    assert "client_id=client-id" in oauth.authorize_url(state="state")
    token = oauth.exchange_code("code")
    user = oauth.get_user(token)

    assert user["login"] == "alice"

