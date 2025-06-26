from datetime import datetime, timedelta, date
import pandas as pd
import random

# 1. 기본 설정
start_date = datetime(2025, 4, 14)
end_date = datetime(2025, 5, 10)
days_range = (end_date - start_date).days + 1

# 좌석 정보
seat_info = []
for i in range(1, 5):  # 4인석
    seat_info.append((f"S{i}", 4, "four_seat"))
for i in range(5, 10):  # 2인석
    seat_info.append((f"S{i}", 2, "two_seat"))
seat_info_df = pd.DataFrame(seat_info, columns=["seat_id", "capacity", "zone"])

# 공휴일 지정
holidays = {
    date(2025, 5, 1),  # 근로자의 날
    date(2025, 5, 5),  # 어린이날/석가탄신일
    date(2025, 5, 6),  # 임시공휴일
}

# 시간대 가중치 설정 (9시~21시 → 13개 구간)
hour_range = list(range(9, 22))
age_hour_weights = {
    "teen":   [1, 1, 2, 3, 5, 6, 6, 5, 4, 3, 2, 1, 1],
    "20s":    [2, 3, 5, 7, 8, 7, 6, 6, 7, 6, 5, 3, 2],
    "30s":    [3, 4, 5, 7, 7, 6, 5, 4, 5, 4, 3, 2, 1],
    "40s":    [6, 5, 4, 4, 3, 2, 2, 2, 3, 2, 1, 1, 1],
    "50s":    [6, 5, 4, 4, 3, 2, 2, 2, 3, 2, 1, 1, 1],
    "60+":    [6, 5, 4, 4, 3, 2, 2, 2, 3, 2, 1, 1, 0],
}

# 초기화
people_log, seat_status, wait_log, anomaly_log = [], [], [], []
seat_occupancy = {seat_id: [] for seat_id in seat_info_df["seat_id"]}
person_id_counter = 1
group_id_counter = 1

# 2. 데이터 생성
for day_offset in range(days_range):
    current_day = start_date + timedelta(days=day_offset)
    current_date = current_day.date()
    is_weekend = current_day.weekday() >= 5 or current_date in holidays
    num_customers = random.randint(130, 180) if is_weekend else random.randint(100, 130)

    for _ in range(num_customers):
        person_id = person_id_counter
        person_id_counter += 1

        # 연령, 성별, 방문 시간
        age_group = random.choices(
            ["teen", "20s", "30s", "40s", "50s", "60+"],
            weights=[10, 30, 25, 10, 15, 10]
        )[0]
        gender = random.choice(["M", "F"])
        hour = random.choices(hour_range, weights=age_hour_weights[age_group])[0]
        minute = random.randint(0, 59)
        entry_time = datetime(current_day.year, current_day.month, current_day.day, hour, minute)

        # 영업시간 내 방문만 허용: 9시~22시
        if entry_time.hour < 9 or (entry_time.hour == 22 and entry_time.minute > 0):
            continue

        # 21시 30분 이후: 테이크아웃만 가능
        if entry_time.hour >= 21 and entry_time.minute >= 30:
            person_type = "takeout"
        else:
            # 테이크아웃 확률 (평일/주말 구분)
            takeout_prob = 0.30 if is_weekend else 0.20
            person_type = random.choices(["dine-in", "takeout"], weights=[1 - takeout_prob, takeout_prob])[0]

        if person_type == "takeout":
            duration = random.randint(2, 8)
            exit_time = entry_time + timedelta(minutes=duration)
            people_log.append((person_id, entry_time, "enter", "NULL", age_group, gender, duration, "takeout"))
            people_log.append((person_id, exit_time, "exit", "NULL", age_group, gender, duration, "takeout"))
            continue

        # 매장 이용자 로직
        duration = random.randint(15, 120)
        group_size = random.randint(1, 4)
        exit_time = entry_time + timedelta(minutes=duration)
        zone_pref = random.choice(["four_seat", "two_seat"])

        people_log.append((person_id, entry_time, "enter", zone_pref, age_group, gender, "NULL", "dine-in"))

        # 좌석 배정
        available_seats = seat_info_df[
            (seat_info_df["zone"] == zone_pref) & (seat_info_df["capacity"] >= group_size)
        ]
        assigned = False
        for _, seat in available_seats.iterrows():
            seat_id = seat["seat_id"]
            conflict = any(
                (entry_time < occ['exit_time'] and exit_time > occ['entry_time'])
                for occ in seat_occupancy[seat_id]
            )
            if not conflict:
                seat_occupancy[seat_id].append({"entry_time": entry_time, "exit_time": exit_time})
                seat_status.append((
                    seat_id, entry_time, 1, person_id, zone_pref,
                    seat["capacity"], group_size, group_id_counter
                ))
                assigned = True
                break

        if assigned:
            stay_time = entry_time + timedelta(minutes=duration // 2)
            people_log.append((person_id, stay_time, "stay", zone_pref, age_group, gender, duration, "dine-in"))
            people_log.append((person_id, exit_time, "exit", zone_pref, age_group, gender, duration, "dine-in"))
        else:
            wait_time = random.randint(5, 20)
            wait_end = entry_time + timedelta(minutes=wait_time)
            wait_log.append((person_id, entry_time, wait_end, wait_time, "No available seats"))
            people_log.append((person_id, entry_time, "wait", zone_pref, age_group, gender, "NULL", "dine-in"))

        if duration >= 90:
            anomaly_log.append((person_id, entry_time, zone_pref, "long_stay", "High"))
        elif duration < 20:
            anomaly_log.append((person_id, entry_time, zone_pref, "short_stay", "Medium"))

        group_id_counter += 1

# 3. DataFrame 생성
people_log_df = pd.DataFrame(people_log, columns=["person_id", "timestamp", "event_type", "zone", "age_group", "gender", "duration", "person_type"])
seat_status_df = pd.DataFrame(seat_status, columns=["seat_id", "timestamp", "is_occupied", "person_id", "zone", "capacity", "current_count", "group_id"])
wait_log_df = pd.DataFrame(wait_log, columns=["person_id", "start_time", "end_time", "wait_duration", "reason"])
anomaly_log_df = pd.DataFrame(anomaly_log, columns=["person_id", "timestamp", "zone", "type", "severity"])

# 예: 저장
people_log_df.to_csv("C:/Users/people_log.csv", index=False)
seat_status_df.to_csv("C:/Users/seat_status.csv", index=False)
wait_log_df.to_csv("C:/Users/wait_log.csv", index=False)
anomaly_log_df.to_csv("C:/Users/anomaly_log.csv", index=False)
seat_info_df.to_csv("C:/Users/seat_info.csv", index=False)
