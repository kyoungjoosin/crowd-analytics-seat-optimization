import streamlit as st
import pandas as pd
import numpy as np
import pickle

# 모델 로드 
@st.cache_data(show_spinner=False)
def load_model():
    with open('rf_model.pkl', 'rb') as f:
        model, model_features = pickle.load(f)
    return model, model_features

def preprocess_input(df_input):
    weekday_map = {1: 'Monday', 2: 'Tuesday', 3: 'Wednesday',
                   4: 'Thursday', 5: 'Friday', 6: 'Saturday', 7: 'Sunday'}

    df = df_input.copy()
    
    df['queue_enter_time'] = pd.to_datetime(df['queue_enter_time'])
    df['date'] = pd.to_datetime(df['queue_enter_time'].dt.date)
    df['weekday'] = df['queue_enter_time'].dt.dayofweek + 1
    df['weekday_name'] = df['weekday'].map(weekday_map)
    df['is_weekend'] = df['weekday_name'].isin(['Saturday', 'Sunday']).astype(int)

    public_holidays = ['2025-05-01', '2025-05-05', '2025-05-06']
    df['is_holiday'] = df['date'].astype(str).isin(public_holidays).astype(int)

    df['hour'] = df['queue_enter_time'].dt.hour
    df['hour_int'] = df['hour'].astype(int)
    df['is_am'] = (df['hour_int'] < 12).astype(int)
    df['is_pm'] = (df['hour_int'] >= 12).astype(int)

    df['hour_sin'] = np.sin(2 * np.pi * df['hour_int'] / 24)
    df['hour_cos'] = np.cos(2 * np.pi * df['hour_int'] / 24)

    # visitor_count : 동시간대 방문자 수, concurrent_wait_count : 대기 중인 사람 수
    df['datetime_hour'] = df['queue_enter_time'].dt.floor('H')
    visitor_counts = df.groupby('datetime_hour')['person_id'].transform('count')
    df['visitor_count'] = visitor_counts
    df['concurrent_wait_count'] = df.groupby('datetime_hour')['wait_duration'].transform('count')

    df = df.sort_values('queue_enter_time')
    df['rolling_wait_mean'] = df['wait_duration'].rolling(window=10, min_periods=1).mean()

    df['is_morning_rush'] = df['hour_int'].between(7, 9).astype(int)
    df['is_lunch_time'] = df['hour_int'].between(12, 13).astype(int)
    df['is_evening_rush'] = df['hour_int'].between(17, 19).astype(int)

    df['prev_wait'] = df['wait_duration'].shift(1).fillna(df['wait_duration'].mean())
    df['wait_diff'] = df['wait_duration'].diff().fillna(0)

    df[['person_type', 'age_group', 'gender']] = df[['person_type', 'age_group', 'gender']].astype(str)

    return df

def predict_wait_duration(df_input, model, model_features):
    df = preprocess_input(df_input)

    features = [
        'weekday_name', 'hour', 'person_type', 'age_group', 'gender',
        'is_weekend', 'is_holiday',
        'visitor_count', 'concurrent_wait_count',
        'is_am', 'is_pm', 'hour_sin', 'hour_cos',
        'rolling_wait_mean',
        'is_morning_rush', 'is_lunch_time', 'is_evening_rush',
        'prev_wait', 'wait_diff'
    ]

    df_encoded = pd.get_dummies(df[features], drop_first=True)

    for col in model_features:
        if col not in df_encoded.columns:
            df_encoded[col] = 0
    df_encoded = df_encoded[model_features]

    y_pred = model.predict(df_encoded)

    df_result = df_input.copy()
    df_result['predicted_wait_duration'] = y_pred
    return df_result

def main():
    st.title("대기시간 예측 (RandomForest)")

    st.write("입력 값을 넣으면 대기시간을 예측해줍니다.")

    person_id = st.text_input("Person ID", "1234")
    queue_enter_time = st.text_input("Queue Enter Time (YYYY-MM-DD HH:MM:SS)", "2025-06-21 08:30:00")
    wait_duration = st.number_input("Wait Duration (실제 대기시간 입력, 모를 땐 평균값 대체)", min_value=0.0, value=3.5)
    person_type = st.selectbox("Person Type", ["customer", "staff", "visitor"])
    age_group = st.selectbox("Age Group", ["20-30", "30-40", "40-50", "50+"])
    gender = st.selectbox("Gender", ["M", "F"])

    if st.button("예측하기"):
        try:
            input_df = pd.DataFrame({
                'person_id': [person_id],
                'queue_enter_time': [pd.to_datetime(queue_enter_time)],
                'wait_duration': [wait_duration],
                'person_type': [person_type],
                'age_group': [age_group],
                'gender': [gender],
                'enter_time': [pd.to_datetime(queue_enter_time)]  
            })

            model, model_features = load_model()
            result = predict_wait_duration(input_df, model, model_features)
            st.success(f"예측 대기시간: {result['predicted_wait_duration'].values[0]:.2f} 분")
        except Exception as e:
            st.error(f"에러 발생: {e}")

if __name__ == "__main__":
    main()