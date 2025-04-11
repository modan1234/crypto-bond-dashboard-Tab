import pandas as pd

def crawl_naver_busan_apartments():
    # 실제 구현 전 임시 테스트용 더미 데이터 반환
    data = {
        "단지명": ["센텀푸르지오", "수영롯데캐슬", "센텀푸르지오", "수영롯데캐슬"],
        "공급면적": [115.0, 114.0, 115.0, 114.0],
        "전용면적": [84.9, 84.1, 84.9, 84.1],
        "전세가": [55000, 54000, 55000, 54000],
        "월세가": [1300, 1200, 1300, 1200],
    }
    df = pd.DataFrame(data)
    df.drop_duplicates(inplace=True)  # 중복 매물 제거
    df = df[df["공급면적"] <= 115]     # 35평 이하만 (약 115㎡ 이하)
    return df
