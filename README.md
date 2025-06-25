# 카페 혼잡도 분석 및 좌석 최적화 시스템

> **카페 방문 로그 데이터를 기반으로, 요일/시간대별 혼잡도 분석 및 대기시간 예측 모델을 통해 운영 효율을 높이는 분석 프로젝트입니다.**

---

## 🔍 프로젝트 개요

- **목표**: 요일·시간대별 방문자 흐름 및 대기시간 데이터를 분석해, 혼잡도를 파악하고 좌석 배치를 최적화
- **데이터**: CCTV 기반 방문 로그 (`people_log`), 대기시간 로그 (`wait_log`)  
- **활용 기술**: Python (pandas, sklearn, matplotlib, seaborn 등), MySQL, Jupyter Notebook

---

## 📊 분석 흐름

1. **데이터 수집 및 정제**
   - MySQL에서 `people_log`, `wait_log` 테이블 조인
   - 요일, 시간대, 인구 통계 정보(연령/성별/이용유형) 가공

2. **탐색적 데이터 분석 (EDA)**
   - 요일/시간대별 방문자 수 시각화 (히트맵)
   - 시간대별 평균 대기시간 분석
   - 테이크아웃 vs 매장 이용 비율 비교
   - 혼잡도 구간화 (`Low / Mid / High`) 및 시각화

3. **대기시간 예측 모델링**
   - 주요 피처: 요일, 시간대, 성별, 연령대, person_type 등
   - 모델: Random Forest Regressor
   - 평가 지표: MAE / RMSE / R² Score

4. **운영 전략 제안**
   - 혼잡 시간대 좌석 재배치 or 체류시간 제한 정책 시뮬레이션 *(추가 예정)*

---

## 🧪 결과 요약

- 대기시간 예측 R² Score: **0.98**
- 특정 요일/시간대에 혼잡도 집중 현상 확인
- 예측값 기반으로 시간대별 운영 전략 수립 가능

---

## 🗂️ 디렉토리 구조

crowd-analytics-seat-optimization/
├── README.md
├── requirements.txt
├── data/
│   └── sample_schema_description.md
├── notebooks/
│   ├── 01_eda.ipynb
│   ├── 02_feature_engineering.ipynb
│   └── 03_model_training.ipynb
├── scripts/
│   ├── utils.py
│   └── model_pipeline.py
└── results/
    ├── heatmaps/
    └── metrics/


---

## ⚙️ 사용 기술

- **Python**: pandas, seaborn, matplotlib, scikit-learn
- **DB**: MySQL
- **IDE**: Jupyter Notebook
- **배포 예정**: Streamlit (대기시간 실시간 예측 앱)

---

## 📌 프로젝트 보기

> 깃허브 주소: [https://github.com/kyoungjoosin/crowd-analytics-seat-optimization](https://github.com/kyoungjoosin/crowd-analytics-seat-optimization)

---

## 🙋‍♀️ 작성자

- **Name**: Shin KyoungJoo 
- **Contact**: kyoungjoosin@gmail.com

