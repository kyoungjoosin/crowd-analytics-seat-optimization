import streamlit as st
import pandas as pd
import numpy as np
import pickle
from sqlalchemy import create_engine
from datetime import datetime

# 1. DB 연결 설정 (본인 DB 정보로 변경)
engine = create_engine('mysql+pymysql://root:rudwn0568!@localhost/Project1')

# 2. 저장된 모델 불러오기
with open('rf_model.pkl', 'rb') as f:
    model = pickle.load(f)

# 3. 사용자 입력 받기
date_input = st.date_input("예측할 날짜 선택")
hour_input = st.number_input("예측할 시간 입력 (0~23)", min_value=0, max_value=23, value=13)

def fetch_features_from_db(date, hour):
    # 날짜와 시간 기준으로 임의 피처 조회 쿼리 예시 (필요에 맞게 조정)
    weekday = (date.weekday() + 1)  # 월=1, ..., 일=7 (필요시 조정)
    date_str = date.strftime('%Y-%m-%d')

    query = f"""
    SELECT 
        AVG(visitor_count) AS visitor_count,
        AVG(concurrent_wait_count) AS concurrent_wait_count,
        AVG(rolling_wait_mean) AS rolling_wait_mean,
        AVG(prev_wait) AS prev_wait,
        AVG(wait_diff) AS wait_diff
    FROM feature_stats_table
    WHERE weekday = {weekday} AND hour = {hour} AND date <= '{date_str}'
    """

    result = pd.read_sql(query, engine)

    # 결과가 없으면 기본값 설정
    if result.empty or result.isnull().values.any():
        return {
            'visitor_count': 10,
            'concurrent_wait_count': 5,
            'rolling_wait_mean': 2.5,
            'prev_wait': 2.5,
            'wait_diff': 0,
        }
    else:
        row = result.iloc[0]
        return {
            'visitor_count': row['visitor_count'],
            'concurrent_wait_count': row['concurrent_wait_count'],
            'rolling_wait_mean': row['rolling_wait_mean'],
            'prev_wait': row['prev_wait'],
            'wait_diff': row['wait_diff'],
        }

def create_features(date, hour):
    df = pd.DataFrame({'date': [pd.to_datetime(date)], 'hour': [hour]})
    df['weekday'] = df['date'].dt.dayofweek + 1  # 월=1, ... 일=7
    weekday_map = {1:'Monday',2:'Tuesday',3:'Wednesday',4:'Thursday',5:'Friday',6:'Saturday',7:'Sunday'}
    df['weekday_name'] = df['weekday'].map(weekday_map)

    df['is_weekend'] = df['weekday_name'].isin(['Saturday', 'Sunday']).astype(int)
    public_holidays = ['2025-05-01', '2025-05-05', '2025-05-06']
    df['is_holiday'] = df['date'].astype(str).isin(public_holidays).astype(int)

    # 시간 사이클릭 인코딩
    df['hour_sin'] = np.sin(2 * np.pi * hour / 24)
    df['hour_cos'] = np.cos(2 * np.pi * hour / 24)

    # 출퇴근, 점심시간 플래그
    df['is_morning_rush'] = int(7 <= hour <= 9)
    df['is_lunch_time'] = int(12 <= hour <= 13)
    df['is_evening_rush'] = int(17 <= hour <= 19)

    # DB에서 임의 피처 조회
    stats = fetch_features_from_db(date, hour)

    for key, value in stats.items():
        df[key] = value

    # 범주형 변수 예시 (필요시 실제값으로 변경)
    df['person_type'] = 'type1'
    df['age_group'] = '30-40'
    df['gender'] = 'F'

    # One-hot 인코딩
    df = pd.get_dummies(df)

    # 모델에 맞는 피처 컬럼 정렬 및 부족한 컬럼 0 채우기
    feature_cols = model.feature_names_in_ if hasattr(model, 'feature_names_in_') else df.columns
    df = df.reindex(columns=feature_cols, fill_value=0)

    return df

if st.button('대기시간 예측'):
    features = create_features(date_input, hour_input)
    pred = model.predict(features)[0]
    st.write(f"예상 대기시간: {pred:.2f}분")