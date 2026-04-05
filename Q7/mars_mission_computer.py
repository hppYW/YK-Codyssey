import random
import datetime
import json
import time
import threading


class DummySensor:
    def __init__(self):
        # 환경 데이터를 저장하는 사전 (초기값 0)
        self.env_values = {
            'mars_base_internal_temperature': 0,
            'mars_base_external_temperature': 0,
            'mars_base_internal_humidity': 0,
            'mars_base_external_illuminance': 0,
            'mars_base_internal_co2': 0,
            'mars_base_internal_oxygen': 0,
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

        # 로그 파일에 추가 기록
        log_line = (
            f'{now}, '
            f'{self.env_values["mars_base_internal_temperature"]}, '
            f'{self.env_values["mars_base_external_temperature"]}, '
            f'{self.env_values["mars_base_internal_humidity"]}, '
            f'{self.env_values["mars_base_external_illuminance"]}, '
            f'{self.env_values["mars_base_internal_co2"]}, '
            f'{self.env_values["mars_base_internal_oxygen"]}\n'
        )

        with open('mars_mission_computer.log', 'a') as log_file:
            log_file.write(log_line)

        # 현재 환경 데이터 반환
        return self.env_values


class MissionComputer:
    def __init__(self):
        # DummySensor 클래스를 ds라는 이름으로 인스턴스화
        self.ds = DummySensor()

        # 화성 기지 환경 값을 저장하는 사전
        self.env_values = {
            'mars_base_internal_temperature': 0,
            'mars_base_external_temperature': 0,
            'mars_base_internal_humidity': 0,
            'mars_base_external_illuminance': 0,
            'mars_base_internal_co2': 0,
            'mars_base_internal_oxygen': 0,
        }

        # 종료 플래그
        self.stop_flag = False

        # 5분 평균 계산을 위한 데이터 저장 리스트
        self.history = []

    def _input_listener(self):
        # 별도 스레드에서 키 입력을 대기하는 메소드
        while not self.stop_flag:
            user_input = input()
            if user_input.lower() == 'q':
                self.stop_flag = True
                break

    def _print_average(self):
        # 5분 평균값을 계산하여 출력하는 메소드
        if not self.history:
            return

        avg_values = {}
        for key in self.env_values:
            total = sum(record[key] for record in self.history)
            avg_values[key] = round(total / len(self.history), 4)

        print('\n===== 5분 평균 환경 값 =====')
        print(json.dumps(avg_values, indent=4))
        print('============================\n')

        # 평균 출력 후 기록 초기화
        self.history.clear()

    def get_sensor_data(self):
        # 입력 감지 스레드 시작
        input_thread = threading.Thread(target=self._input_listener, daemon=True)
        input_thread.start()

        print('센서 데이터 수집을 시작합니다. 종료하려면 q를 입력하세요.')

        # 5분 평균 계산을 위한 시간 기록
        last_avg_time = time.time()

        while not self.stop_flag:
            # 센서 값 갱신
            self.ds.set_env()

            # 센서 값을 가져와서 env_values에 담기
            sensor_data = self.ds.get_env()
            self.env_values.update(sensor_data)

            # 5분 평균 계산을 위해 현재 값 저장
            self.history.append(dict(self.env_values))

            # env_values를 JSON 형태로 출력
            print(json.dumps(self.env_values, indent=4))

            # 5분(300초) 경과 시 평균값 출력
            current_time = time.time()
            if current_time - last_avg_time >= 300:
                self._print_average()
                last_avg_time = current_time

            # 5초 대기 (0.5초 단위로 체크하여 종료 반응 향상)
            for _ in range(10):
                if self.stop_flag:
                    break
                time.sleep(0.5)

        print('System stopped....')


# MissionComputer 클래스를 RunComputer라는 이름으로 인스턴스화
RunComputer = MissionComputer()

# get_sensor_data() 메소드 호출하여 환경 값 지속 출력
RunComputer.get_sensor_data()
