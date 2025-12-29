print("문장을 입력하세요. 종료하려면 '!quit'을 입력하세요.")

while True:
    sentence = input("> ")

    if sentence == "!quit":
        print("프로그램을 종료합니다.")
        break

    print(sentence)
