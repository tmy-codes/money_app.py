scores = input("点数をスペース区切りで入力してください: ")

score_list = list(map(int, scores.split()))

average = sum(score_list) / len(score_list)

print("平均点は", average, "です")
