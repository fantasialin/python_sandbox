year = int(input("請輸入年份："))

if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
    print(year, "是閏年")
else:
    print(year, "不是閏年")