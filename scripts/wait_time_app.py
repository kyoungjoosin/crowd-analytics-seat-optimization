import streamlit as st
import pandas as pd
import numpy as np
import pickle
from sqlalchemy import create_engine
from datetime import datetime
import pytz

# DB 연결 설정
engine = create_engine(f'mysql+pymysql://root:passwd@localhost/Project1')

# 모델 로드
with open('rf_model.pkl', 'rb') as f:
    model, feature_columns = pickle.load(f)

# 공휴일 목록 (필요 시 확장)
public_holidays = ['2025-05-01', '2025-05-05', '2025-05-06']

# Streamlit UI
st.title("실시간 대기시간 예측기")
st.write("날짜와 시간을 선택하면 해당 시간의 예상 대기시간을 예측합니다.")

# 날짜/시간 입력
selected_date = st.date_input("날짜 선택", value=pd.to_datetime("today"))
if "selected_time" not in st.session_state:
    st.session_state.selected_time = datetime.now().replace(second=0, microsecond=0).time()

selected_time = st.time_input("시간 선택", value=st.session_state.selected_time, key="time_input_key")
st.session_state.selected_time = selected_time

# 예측 실행
if st.button("예측하기"):

    # 입력 정보 파싱
    input_datetime = datetime.combine(selected_date, selected_time)
    input_weekday = input_datetime.isoweekday() % 7 + 1  # MySQL 기준으로 일요일=1
    input_hour = input_datetime.hour

    # 쿼리: LAG()를 서브쿼리에서 먼저 계산하고 바깥에서 GROUP BY
    query = f"""
    SELECT
        person_type,
        age_group,
        gender,
        weekday,
        hour,
        date,
        COUNT(person_id) AS visitor_count,
        COUNT(wait_duration) AS concurrent_wait_count,
        AVG(wait_duration) AS rolling_wait_mean,
        AVG(prev_wait) AS prev_wait_avg
    FROM (
        SELECT
            p.person_type,
            p.age_group,
            p.gender,
            DAYOFWEEK(w.start_time) AS weekday,
            HOUR(w.start_time) AS hour,
            DATE(w.start_time) AS date,
            w.person_id,
            w.wait_duration,
            LAG(w.wait_duration) OVER (ORDER BY w.start_time) AS prev_wait
        FROM wait_log w
        INNER JOIN people_log p ON w.person_id = p.person_id
        WHERE p.event_type = 'enter'
          AND HOUR(w.start_time) = {input_hour}
          AND DAYOFWEEK(w.start_time) = {input_weekday}
          AND w.start_time < '{selected_date}'
    ) AS sub
    GROUP BY person_type, age_group, gender, weekday, hour, date
    LIMIT 100
    """

    df_sample = pd.read_sql(query, engine)

    if df_sample.empty:
        st.warning("해당 시간대의 과거 데이터가 부족합니다.")
    else:
        avg_values = df_sample.mean(numeric_only=True)

        sample = pd.DataFrame({
            'weekday_name': [input_datetime.strftime('%A')],
            'hour': [input_hour],
            'person_type': [df_sample['person_type'].mode()[0]],
            'age_group': [df_sample['age_group'].mode()[0]],
            'gender': [df_sample['gender'].mode()[0]],
            'is_weekend': [1 if input_datetime.weekday() >= 5 else 0],
            'is_holiday': [1 if str(selected_date) in public_holidays else 0],
            'visitor_count': [avg_values['visitor_count']],
            'concurrent_wait_count': [avg_values['concurrent_wait_count']],
            'is_am': [1 if input_hour < 12 else 0],
            'is_pm': [1 if input_hour >= 12 else 0],
            'hour_sin': [np.sin(2 * np.pi * input_hour / 24)],
            'hour_cos': [np.cos(2 * np.pi * input_hour / 24)],
            'rolling_wait_mean': [avg_values['rolling_wait_mean']],
            'is_morning_rush': [1 if 7 <= input_hour <= 9 else 0],
            'is_lunch_time': [1 if 12 <= input_hour <= 13 else 0],
            'is_evening_rush': [1 if 17 <= input_hour <= 19 else 0],
            'prev_wait': [avg_values.get('prev_wait_avg', avg_values['rolling_wait_mean'])],
            'wait_diff': [avg_values['rolling_wait_mean'] - avg_values.get('prev_wait_avg', avg_values['rolling_wait_mean'])],
        })

        # One-hot 인코딩 및 누락된 피처 채우기
        sample_encoded = pd.get_dummies(sample)
        for col in feature_columns:
            if col not in sample_encoded.columns:
                sample_encoded[col] = 0
        sample_encoded = sample_encoded[feature_columns]

        # 예측 실행
        prediction = model.predict(sample_encoded)[0]
        st.success(f"예상 대기시간은 약 {prediction:.1f}분입니다.")
