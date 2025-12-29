# password.py
import re

# 알파벳, 숫자, 특수문자 각각 최소 1개 이상 + 전체 길이 6 이상
_PASSWORD_PATTERN = re.compile(
    r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[^A-Za-z0-9]).{6,}$"
)

def is_valid_password(pw: str) -> bool:
    """
    비밀번호 규칙:
    - 길이 6자 이상
    - 알파벳 1개 이상
    - 숫자 1개 이상
    - 특수문자 1개 이상 (알파벳/숫자 제외 문자)
    """
    return bool(_PASSWORD_PATTERN.match(pw))


def password_rules() -> str:
    """사용자에게 보여줄 규칙 안내 문자열"""
    return (
        "비밀번호 규칙:\n"
        "- 최소 6자 이상\n"
        "- 알파벳(A-Z 또는 a-z) 최소 1개 포함\n"
        "- 숫자(0-9) 최소 1개 포함\n"
        "- 특수문자 최소 1개 포함 (예: !@#$%^&*)"
    )


if __name__ == "__main__":
    # 단독 실행 테스트용
    pw = input("비밀번호를 입력하세요: ")
    if is_valid_password(pw):
        print("OK: 사용 가능한 비밀번호입니다.")
    else:
        print("NG: 비밀번호 규칙을 만족하지 않습니다.")
        print(password_rules())
