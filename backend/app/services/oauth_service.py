import urllib.parse
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
import httpx
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.errors import AppException
from app.core.security import create_access_token, hash_password
from app.models.oauth import OAuthConnection
from app.models.profile import StudentProfile
from app.models.user import User
from app.schemas.auth import OAuthLoginRequest, OAuthUrlOut

GOOGLE_SCOPES = [
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/calendar.events",
    "https://www.googleapis.com/auth/gmail.readonly",
]

GITHUB_SCOPES = [
    "read:user",
    "user:email",
]


class OAuthService:
    def get_oauth_url(self, provider: str, redirect_uri: Optional[str] = None) -> OAuthUrlOut:
        provider = provider.lower()
        if provider == "google":
            target_redirect = redirect_uri or settings.GOOGLE_REDIRECT_URI
            if not settings.GOOGLE_CLIENT_ID:
                mock_url = f"{target_redirect}?code=mock_google_code_{uuid.uuid4().hex[:8]}&provider=google"
                return OAuthUrlOut(provider="google", auth_url=mock_url, is_mock=True)

            params = {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "redirect_uri": target_redirect,
                "response_type": "code",
                "scope": " ".join(GOOGLE_SCOPES),
                "access_type": "offline",
                "prompt": "consent",
                "state": f"google_{uuid.uuid4().hex[:8]}",
            }
            url = f"https://accounts.google.com/o/oauth2/v2/auth?{urllib.parse.urlencode(params)}"
            return OAuthUrlOut(provider="google", auth_url=url, is_mock=False)

        elif provider == "github":
            target_redirect = redirect_uri or settings.GITHUB_REDIRECT_URI
            if not settings.GITHUB_CLIENT_ID:
                mock_url = f"{target_redirect}?code=mock_github_code_{uuid.uuid4().hex[:8]}&provider=github"
                return OAuthUrlOut(provider="github", auth_url=mock_url, is_mock=True)

            params = {
                "client_id": settings.GITHUB_CLIENT_ID,
                "redirect_uri": target_redirect,
                "scope": " ".join(GITHUB_SCOPES),
                "state": f"github_{uuid.uuid4().hex[:8]}",
            }
            url = f"https://github.com/login/oauth/authorize?{urllib.parse.urlencode(params)}"
            return OAuthUrlOut(provider="github", auth_url=url, is_mock=False)

        else:
            raise AppException(
                message=f"Unsupported OAuth provider: {provider}",
                code="INVALID_PROVIDER",
                status_code=400,
            )

    def authenticate_social_user(
        self, db: Session, request: OAuthLoginRequest
    ) -> Tuple[User, str]:
        email = request.email.lower().strip()
        provider = request.provider.lower().strip()
        full_name = (request.full_name or email.split("@")[0].replace(".", " ").title()).strip()

        # 1. Find or create user
        user = db.query(User).filter(User.email == email).first()
        if not user:
            user = User(
                email=email,
                full_name=full_name,
                hashed_password=hash_password(f"oauth_{uuid.uuid4().hex}"),
                is_active=True,
            )
            db.add(user)
            db.flush()

            # Initialize empty student profile
            profile = StudentProfile(user_id=user.id)
            db.add(profile)
            db.flush()
        else:
            if not user.is_active:
                raise AppException(
                    message="This account is currently disabled.",
                    code="ACCOUNT_INACTIVE",
                    status_code=403,
                )
            if not user.full_name and full_name:
                user.full_name = full_name

        # 2. Upsert OAuth connection record
        conn = (
            db.query(OAuthConnection)
            .filter(
                OAuthConnection.user_id == user.id,
                OAuthConnection.provider == provider,
            )
            .first()
        )
        
        access_token_val = request.access_token or request.id_token or f"mock_{provider}_token_{uuid.uuid4().hex[:12]}"
        expires_at_val = datetime.now(timezone.utc) + timedelta(days=30)
        scopes_list = GOOGLE_SCOPES if provider == "google" else GITHUB_SCOPES

        if not conn:
            conn = OAuthConnection(
                user_id=user.id,
                provider=provider,
                email=email,
                access_token=access_token_val,
                refresh_token=None,
                scopes=scopes_list,
                expires_at=expires_at_val,
                status="CONNECTED",
                is_mock=request.access_token is None,
            )
            db.add(conn)
        else:
            conn.email = email
            conn.access_token = access_token_val
            conn.expires_at = expires_at_val
            conn.status = "CONNECTED"

        db.commit()
        db.refresh(user)

        # 3. Issue JWT Token
        jwt_token = create_access_token(subject=user.id)
        return user, jwt_token

    def exchange_code(
        self,
        db: Session,
        provider: str,
        code: str,
        redirect_uri: Optional[str] = None,
    ) -> Tuple[User, str]:
        provider = provider.lower().strip()
        
        is_mock = (
            code.startswith("mock_")
            or (provider == "google" and (not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET))
            or (provider == "github" and (not settings.GITHUB_CLIENT_ID or not settings.GITHUB_CLIENT_SECRET))
        )

        if is_mock:
            suffix = code.split("_")[-1] if "_" in code else uuid.uuid4().hex[:6]
            if provider == "google":
                email = f"google.user.{suffix}@gmail.com"
                full_name = f"Google User {suffix.upper()}"
            elif provider == "github":
                email = f"github.user.{suffix}@github.com"
                full_name = f"GitHub Developer {suffix.upper()}"
            else:
                email = f"{provider}.user.{suffix}@example.com"
                full_name = f"{provider.capitalize()} User"

            return self.authenticate_social_user(
                db,
                OAuthLoginRequest(
                    provider=provider,
                    email=email,
                    full_name=full_name,
                    access_token=f"mock_{provider}_token_{code}",
                ),
            )

        # Live OAuth Exchange
        if provider == "google":
            target_redirect = redirect_uri or settings.GOOGLE_REDIRECT_URI
            try:
                with httpx.Client(timeout=10.0) as client:
                    resp = client.post(
                        "https://oauth2.googleapis.com/token",
                        data={
                            "code": code,
                            "client_id": settings.GOOGLE_CLIENT_ID,
                            "client_secret": settings.GOOGLE_CLIENT_SECRET,
                            "redirect_uri": target_redirect,
                            "grant_type": "authorization_code",
                        },
                    )
                    resp.raise_for_status()
                    token_data = resp.json()
                    access_token = token_data.get("access_token")

                    userinfo_resp = client.get(
                        "https://www.googleapis.com/oauth2/v2/userinfo",
                        headers={"Authorization": f"Bearer {access_token}"},
                    )
                    userinfo_resp.raise_for_status()
                    userinfo = userinfo_resp.json()
                    email = userinfo.get("email")
                    name = userinfo.get("name") or email.split("@")[0]

                    return self.authenticate_social_user(
                        db,
                        OAuthLoginRequest(
                            provider="google",
                            email=email,
                            full_name=name,
                            access_token=access_token,
                            id_token=token_data.get("id_token"),
                        ),
                    )
            except Exception as e:
                raise AppException(
                    message=f"Failed to authenticate with Google: {str(e)}",
                    code="GOOGLE_AUTH_FAILED",
                    status_code=400,
                )

        elif provider == "github":
            target_redirect = redirect_uri or settings.GITHUB_REDIRECT_URI
            try:
                with httpx.Client(timeout=10.0) as client:
                    resp = client.post(
                        "https://github.com/login/oauth/access_token",
                        headers={"Accept": "application/json"},
                        data={
                            "client_id": settings.GITHUB_CLIENT_ID,
                            "client_secret": settings.GITHUB_CLIENT_SECRET,
                            "code": code,
                            "redirect_uri": target_redirect,
                        },
                    )
                    resp.raise_for_status()
                    token_data = resp.json()
                    access_token = token_data.get("access_token")

                    # Get user profile
                    user_resp = client.get(
                        "https://api.github.com/user",
                        headers={
                            "Authorization": f"Bearer {access_token}",
                            "Accept": "application/vnd.github.v3+json",
                        },
                    )
                    user_resp.raise_for_status()
                    userinfo = user_resp.json()

                    email = userinfo.get("email")
                    if not email:
                        # Fetch emails if primary email is private
                        emails_resp = client.get(
                            "https://api.github.com/user/emails",
                            headers={
                                "Authorization": f"Bearer {access_token}",
                                "Accept": "application/vnd.github.v3+json",
                            },
                        )
                        if emails_resp.status_code == 200:
                            for em in emails_resp.json():
                                if em.get("primary") and em.get("verified"):
                                    email = em.get("email")
                                    break
                                elif not email and em.get("email"):
                                    email = em.get("email")

                    if not email:
                        login_handle = userinfo.get("login", "developer")
                        email = f"{login_handle}@users.noreply.github.com"

                    name = userinfo.get("name") or userinfo.get("login") or email.split("@")[0]

                    return self.authenticate_social_user(
                        db,
                        OAuthLoginRequest(
                            provider="github",
                            email=email,
                            full_name=name,
                            access_token=access_token,
                            provider_user_id=str(userinfo.get("id")),
                        ),
                    )
            except Exception as e:
                raise AppException(
                    message=f"Failed to authenticate with GitHub: {str(e)}",
                    code="GITHUB_AUTH_FAILED",
                    status_code=400,
                )

        raise AppException(
            message=f"Unsupported OAuth provider: {provider}",
            code="INVALID_PROVIDER",
            status_code=400,
        )


oauth_service = OAuthService()
