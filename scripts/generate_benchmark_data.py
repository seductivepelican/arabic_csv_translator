import pandas as pd
import random

def generate_benchmark_csv(filename, num_rows):
    titles = [
        "تقرير اللجنة المالية",
        "محضر اجتماع مجلس الإدارة",
        "مذكرة تفاهم بين الطرفين",
        "قرار وزاري رقم ١٢٣",
        "بيان ختامي للمؤتمر",
        "وثيقة رسمية سرية",
        "خطاب طلب تمديد",
        "تقرير الأداء السنوي",
        "اتفاقية تعاون مشترك",
        "ملخص التنفيذي للمشروع"
    ]
    data = []
    for i in range(num_rows):
        data.append({
            "id": i + 1,
            "arabic_text": random.choice(titles)
        })
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    print(f"Generated {filename} with {num_rows} rows.")

if __name__ == "__main__":
    generate_benchmark_csv("benchmark_10.csv", 10)
    generate_benchmark_csv("benchmark_100.csv", 100)
    generate_benchmark_csv("benchmark_1000.csv", 1000)
