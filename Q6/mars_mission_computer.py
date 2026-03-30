import random
import datetime


class DummySensor:
    def __init__(self):
        # 환경 데이터를 저장하는 사전 (초기값 0)
        self.env_values = {
            'mars_base_internal_temperature': 0,  # 내부 온도 (도)
            'mars_base_external_temperature': 0,  # 외부 온도 (도)
            'mars_base_internal_humidity': 0,     # 내부 습도 (%)
            'mars_base_external_illuminance': 0,  # 외부 광량 (W/m2)
            'mars_base_internal_co2': 0,          # 내부 이산화탄소 농도 (%)
            'mars_base_internal_oxygen': 0,       # 내부 산소 농도 (%)
        }

    def set_env(self):
        # 각 항목을 지정된 범위 내 랜덤값으로 설정
        self.env_values['mars_base_internal_temperature'] = round(random.uniform(18, 30), 2)
        self.env_values['mars_base_external_temperature'] = round(random.uniform(0, 21), 2)
        self.env_values['mars_base_internal_humidity'] = round(random.uniform(50, 60), 2)
        self.env_values['mars_base_external_illuminance'] = round(random.uniform(500, 715), 2)
        self.env_values['mars_base_internal_co2'] = round(random.uniform(0.02, 0.1), 4)
        self.env_values['mars_base_internal_oxygen'] = round(random.uniform(4, 7), 2)

    def get_env(self):
        # 현재 날짜와 시간
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # 로그 내용 구성
        log_line = (
            f'{now}, '
            f'{self.env_values["mars_base_internal_temperature"]}, '
            f'{self.env_values["mars_base_external_temperature"]}, '
            f'{self.env_values["mars_base_internal_humidity"]}, '
            f'{self.env_values["mars_base_external_illuminance"]}, '
            f'{self.env_values["mars_base_internal_co2"]}, '
            f'{self.env_values["mars_base_internal_oxygen"]}\n'
        )

        # 로그 파일에 추가 기록
        with open('mars_mission_computer.log', 'a') as log_file:
            log_file.write(log_line)

        # 현재 환경 데이터 반환
        return self.env_values


ds = DummySensor()
ds.set_env()

# 환경 데이터를 항목별로 줄바꿈하여 출력
for key, value in ds.get_env().items():
    print(f'{key}: {value}')
