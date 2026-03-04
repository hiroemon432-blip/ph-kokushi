import pandas as pd
import numpy as np

# Comprehensive list of universities
universities = [
    "東北大学", "京都大学", "千葉大学", "九州大学", "長崎大学", "金沢大学", "広島大学", "富山大学", 
    "静岡県立大学", "名古屋市立大学", "東京大学", "岡山大学", "熊本大学", "徳島大学", "大阪大学", 
    "北海道大学", "岐阜薬科大学", "山陽小野田市立山口東京理科大学", "近畿大学", "九州医療科学大学", 
    "北里大学", "立命館大学", "福岡大学", "高崎健康福祉大学", "国際医療福祉大学", "金城学院大学", 
    "名城大学", "就実大学", "日本大学", "京都薬科大学", "昭和大学", "東京理科大学", "帝京大学", 
    "慶應義塾大学", "武蔵野大学", "星薬科大学", "横浜薬科大学", "崇城大学", "明治薬科大学", 
    "徳島文理大学", "大阪医科薬科大学", "北海道科学大学", "武庫川女子大学", "東北医科薬科大学", 
    "愛知学院大学", "神戸薬科大学", "城西大学", "昭和薬科大学", "第一薬科大学", "摂南大学", 
    "福山大学", "北陸大学", "奥羽大学", "大阪大谷大学", "北海道医療大学", "広島国際大学", 
    "帝京平成大学", "同志社女子大学", "神戸学院大学", "新潟薬科大学", "日本薬科大学", 
    "城西国際大学", "千葉科学大学", "東京薬科大学", "北里大学", "昭和薬科大学", "武蔵野大学",
    "医療創生大学", "九州保健福祉大学", "青森大学", "広島国際大学", "松山大学", "安田女子大学",
    "岩手医科大学", "奥羽大学", "東邦大学"
]

universities = sorted(list(set(universities)))
years = [2020, 2021, 2022, 2023, 2024, 2025]
data = []

# Base data for some top/major universities
base_stats = {
    "名城大学": {"PassRate": 94.0, "ApplicantsRange": (200, 300)},
    "東京大学": {"PassRate": 85.0, "ApplicantsRange": (10, 25)},
    "東北大学": {"PassRate": 95.0, "ApplicantsRange": (20, 35)},
    "京都大学": {"PassRate": 92.0, "ApplicantsRange": (15, 35)},
    "慶應義塾大学": {"PassRate": 85.0, "ApplicantsRange": (130, 170)},
    "北里大学": {"PassRate": 90.0, "ApplicantsRange": (240, 320)},
    "東京理科大学": {"PassRate": 92.0, "ApplicantsRange": (70, 130)},
    "千葉大学": {"PassRate": 93.0, "ApplicantsRange": (40, 60)},
    "金沢大学": {"PassRate": 95.0, "ApplicantsRange": (35, 50)},
    "京都薬科大学": {"PassRate": 88.0, "ApplicantsRange": (300, 450)},
    "日本大学": {"PassRate": 80.0, "ApplicantsRange": (170, 350)},
}

np.random.seed(42)

for univ in universities:
    # Set potential base stats
    if univ in base_stats:
        base_rate = base_stats[univ]["PassRate"]
        app_range = base_stats[univ]["ApplicantsRange"]
    else:
        base_rate = np.random.uniform(55, 85)
        app_range = (50, 250)
    
    for year in years:
        # Yearly factor
        yearly_factor = np.random.normal(0, 2)
        
        # 1. Fresh (新卒) - Usually higher rate
        fresh_rate = np.clip(base_rate + yearly_factor + np.random.normal(2, 1), 50, 100)
        fresh_apps = int(np.random.randint(app_range[0], app_range[1] + 1) * 0.8) # 80% are fresh
        fresh_passers = int(fresh_apps * (fresh_rate / 100.0))
        actual_fresh_rate = round((fresh_passers / fresh_apps) * 100, 2) if fresh_apps > 0 else 0
        
        # 2. Previous (既卒) - Usually lower rate
        prev_rate = np.clip(base_rate * 0.5 + yearly_factor + np.random.normal(-5, 5), 20, 80)
        prev_apps = int(np.random.randint(20, 100))
        prev_passers = int(prev_apps * (prev_rate / 100.0))
        actual_prev_rate = round((prev_passers / prev_apps) * 100, 2) if prev_apps > 0 else 0
        
        # 3. Total (全体)
        total_apps = fresh_apps + prev_apps
        total_passers = fresh_passers + prev_passers
        actual_total_rate = round((total_passers / total_apps) * 100, 2) if total_apps > 0 else 0
        
        for category, apps, passers, rate in [
            ("新卒", fresh_apps, fresh_passers, actual_fresh_rate),
            ("既卒", prev_apps, prev_passers, actual_prev_rate),
            ("全体", total_apps, total_passers, actual_total_rate)
        ]:
            data.append({
                "Year": year,
                "University": univ,
                "Category": category,
                "Applicants": apps,
                "Passers": passers,
                "PassRate": rate
            })

df = pd.DataFrame(data)
df.to_csv("pharmacist_exam_data.csv", index=False)
print(f"Dataset generated with {len(df)} records for {len(universities)} universities across 3 categories.")
