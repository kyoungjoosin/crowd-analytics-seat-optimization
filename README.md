# 📊 카페 혼잡도 분석 및 좌석 최적화 시스템

> CCTV 기반 방문자 로그 데이터를 분석하여  
> 요일·시간대별 혼잡도, 대기시간 예측 모델, 운영 전략 시뮬레이션을 통해  
> **매장 운영 효율을 향상**시키는 데이터 분석 프로젝트입니다.

---

## 🔍 프로젝트 개요

- **목표**: 혼잡도 및 대기시간 분석을 통해 효율적인 좌석 운영 전략 제안
- **분석 대상**: 카페 방문 로그 (`people_log`) + 대기시간 로그 (`wait_log`)
- **활용 기술**: Python (pandas, scikit-learn, seaborn, XGBoost), MySQL, Streamlit

---

## 🧭 분석 흐름

1. **데이터 전처리**
   - MySQL 기반 `people_log`, `wait_log` 조인
   - 요일/시간대/인구통계 기반 파생 피처 생성

2. **탐색적 분석 (EDA)**
   - 요일×시간대별 방문자 분포 시각화
   - 혼잡도 구간화 (분위수 기준) 및 히트맵 작성
   - 고객 체류 유형별 행동 분석

3. **대기시간 예측 모델**
   - 모델: Random Forest Regressor
   - 주요 피처: 시간대, 혼잡도, 이탈자 수 등
   - 성능: R² = 0.996, RMSE = 0.29분

4. **전략 시뮬레이션**
   - 좌석 구성 변경, 체류시간 제한 정책 효과 비교
   - 혼잡 시간대 기준 전략별 성과 수치화

5. **Streamlit 앱 구현**
   - 날짜·시간 입력 시 실시간 대기시간 예측

---

## 🧪 주요 결과 요약

| 항목 | 결과 |
|------|------|
| 📈 대기시간 예측 성능 | RMSE 0.29 / R² 0.996 |
| 🧠 인사이트 | 체류시간 제한 정책이 가장 효과적 |
| 🖥️ 운영 도구화 | Streamlit 기반 실시간 예측 앱 구현 |

---

## ⚙️ 사용 기술

- **Python**: pandas, seaborn, matplotlib, scikit-learn, XGBoost
- **Database**: MySQL
- **IDE**: Jupyter Notebook
- **배포 도구**: Streamlit

---

## 🔗 관련 링크

- 📁 GitHub Repo: [github.com/kyoungjoosin/crowd-analytics-seat-optimization](https://github.com/kyoungjoosin/crowd-analytics-seat-optimization)
- 📄 포트폴리오 Notion: [Project 페이지 보기](https://www.notion.so/Project-211a8d49f8408035b03bd0134b743dd6)

---

## 🙋‍♀️ 작성자

- **Name**: Shin KyoungJoo
- **Email**: kyoungjoosin@gmail.com
- **GitHub**: [@kyoungjoosin](https://github.com/kyoungjoosin)
