# echo.py
from password import is_valid_password, password_rules

def main() -> None:
    print("문장을 입력하세요. 종료하려면 '!quit'을 입력하세요.")
    print("비밀번호 검증을 하려면 '!pw'를 입력하세요.")

    while True:
        text = input("> ")

        if text == "!quit":
            print("프로그램을 종료합니다.")
            break

        if text == "!pw":
            pw = input("비밀번호 입력: ")
            if is_valid_password(pw):
                print("OK: 사용 가능한 비밀번호입니다.")
            else:
                print("NG: 비밀번호 규칙을 만족하지 않습니다.")
                print(password_rules())
            continue

        # 일반 문장은 그대로 출력 (에코)
        print(text)

if __name__ == "__main__":
    main()
