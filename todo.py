tasks = []

while True:
    print("\n--- ToDoアプリ ---")
    print("1: タスク追加")
    print("2: タスク一覧")
    print("3: タスク削除")
    print("4: 終了")

    choice = input("選択してください: ")

    if choice == "1":
        task = input("タスクを入力: ")
        tasks.append(task)
        print("追加しました")

    elif choice == "2":
        if len(tasks) == 0:
            print("タスクはありません")
        else:
            print("\nタスク一覧:")
            for i, t in enumerate(tasks):
                print(f"{i + 1}: {t}")

    elif choice == "3":
        num = int(input("削除する番号: ")) - 1
        if 0 <= num < len(tasks):
            removed = tasks.pop(num)
            print(f"削除しました: {removed}")
        else:
            print("番号が無効です")

    elif choice == "4":
        print("終了します")
        break

    else:
        print("1〜4を入力してください")