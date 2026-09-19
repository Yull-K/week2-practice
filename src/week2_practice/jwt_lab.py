import time
from datetime import datetime, timedelta, timezone

import jwt

SECRET_KEY = "waffle-seminar-week2-secret-key-for-practice"
ALGORITHM = "HS256"


def try_decode(label: str, token: str, key: str = SECRET_KEY) -> None:
    try:
        payload = jwt.decode(token, key, algorithms=[ALGORITHM])
        print(f"[{label}] 검증 성공: {payload}")
    except jwt.InvalidTokenError as e:
        print(f"[{label}] 검증 실패: {type(e).__name__}")


# TODO 1: sub는 "waffle", exp는 지금부터 5초 뒤인 payload를 만들고
#         SECRET_KEY와 HS256으로 서명한 토큰을 token 변수에 담으세요.
payload = {
    "sub": "waffle", # subject ; 사용자 ID
    "exp": datetime.now(timezone.utc) + timedelta(seconds=5)
}
# 다음 2개 위에서 이미 정의해놓음 
# SECRET_KEY: 서명에 쓸 비밀 열쇠 
# algorithm=ALGORITHM (= "HS256"): 서명 계산 방식
token = jwt.encode(payload, SECRET_KEY, algorithm = ALGORITHM)

print("정상토큰 확인")
print("발급된 토큰:", token)
try_decode("정상 토큰", token)

# 실험 1. 다른 비밀키로 검증하기
print("\n 실험 1. 다른 비밀키로 검증하기")
try_decode("다른 키", token, key="not-the-real-secret-key-with-32-or-more-bytes")

# 실험 2. payload의 sub를 "admin"으로 바꾸고 서명은 그대로 두기
# (1) 토큰의 payload는 누구나 읽을 수 있다. 서명 검증 없이 내용만 꺼낸다.
#     실제 서버에서는 절대 이렇게 검증을 끄지 않는다.
print("\n 실험 2. payload의 sub를 admin으로 바꾸고 서명은 그대로 두기")
original = jwt.decode(token, options={"verify_signature": False})
print("원래 payload:", original)

# (2) 공격자는 sub만 "admin"으로 바꾼 토큰을 만든다.
#     진짜 SECRET_KEY를 모르므로 아무 키로나 서명할 수밖에 없다.
attacker_token = jwt.encode(
    original | {"sub": "admin"},
    "attacker-does-not-know-the-real-secret-key",
    algorithm=ALGORITHM,
)

# (3) JWT 토큰은 header.payload.signature 세 부분으로 구성된다.
#     원래 토큰의 header와 signature 사이에 공격자 토큰의 payload만 끼워 넣는다.
header, _, signature = token.split(".")
_, admin_payload, _ = attacker_token.split(".")
tampered = f"{header}.{admin_payload}.{signature}"

print("변조된 payload:", jwt.decode(tampered, options={"verify_signature": False}))
try_decode("sub 변조", tampered)

# 실험 3. JWT 형식이 아닌 문자열
print("\n 실험 3. JWT 형식이 아닌 문자열")
try_decode("형식 오류", "hello-waffle")

# 실험 4. 만료될 때까지 기다리기
print("\n 실험 4. 만료될 때까지 기다리기")
print("6초 기다리는 중...")
time.sleep(6)
try_decode("만료 후", token)