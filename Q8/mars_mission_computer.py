import random
import datetime
import json
import time
import threading
import os
import platform


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

        # setting.txt에서 설정 로드
        self.settings = self._load_settings()

    def _load_settings(self):
        # setting.txt 파일에서 출력 항목 설정을 읽어오는 메소드
        settings = {}
        try:
            with open('setting.txt', 'r') as f:
                for line in f:
                    line = line.strip()
                    if '=' in line:
                        key, value = line.split('=', 1)
                        settings[key.strip()] = value.strip().lower() == 'true'
        except FileNotFoundError:
            # 설정 파일이 없으면 모든 항목 출력
            settings = {
                'os': True,
                'os_version': True,
                'cpu_type': True,
                'cpu_cores': True,
                'memory_size': True,
                'cpu_usage': True,
                'memory_usage': True,
            }
        return settings

    def get_mission_computer_info(self):
        # 미션 컴퓨터의 시스템 정보를 가져오는 메소드
        info = {}

        if self.settings.get('os', True):
            info['os'] = platform.system()

        if self.settings.get('os_version', True):
            info['os_version'] = platform.version()

        if self.settings.get('cpu_type', True):
            info['cpu_type'] = platform.processor()

        if self.settings.get('cpu_cores', True):
            info['cpu_cores'] = os.cpu_count()

        if self.settings.get('memory_size', True):
            # 메모리 크기를 /proc/meminfo 또는 Windows 명령어로 가져오기
            try:
                # Linux 환경
                with open('/proc/meminfo', 'r') as f:
                    for line in f:
                        if line.startswith('MemTotal'):
                            # KB 단위를 GB로 변환
                            mem_kb = int(line.split()[1])
                            info['memory_size'] = f'{round(mem_kb / 1024 / 1024, 2)} GB'
                            break
            except FileNotFoundError:
                # Windows 환경: PowerShell 사용
                try:
                    result = os.popen(
                        'powershell -command "'
                        '(Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory'
                        '"'
                    ).read().strip()
                    if result.isdigit():
                        mem_bytes = int(result)
                        info['memory_size'] = f'{round(mem_bytes / 1024 / 1024 / 1024, 2)} GB'
                    else:
                        info['memory_size'] = 'Unknown'
                except Exception:
                    info['memory_size'] = 'Unknown'

        # JSON 형식으로 출력
        print(json.dumps(info, indent=4, ensure_ascii=False))
        return info

    def get_mission_computer_load(self):
        # 미션 컴퓨터의 실시간 부하 정보를 가져오는 메소드
        load = {}

        if self.settings.get('cpu_usage', True):
            # CPU 사용량 계산 (표준 라이브러리만 사용)
            try:
                # Linux 환경: /proc/stat 사용
                with open('/proc/stat', 'r') as f:
                    first_line = f.readline()
                cpu_times_1 = [int(x) for x in first_line.split()[1:]]
                idle_1 = cpu_times_1[3]
                total_1 = sum(cpu_times_1)

                time.sleep(1)

                with open('/proc/stat', 'r') as f:
                    first_line = f.readline()
                cpu_times_2 = [int(x) for x in first_line.split()[1:]]
                idle_2 = cpu_times_2[3]
                total_2 = sum(cpu_times_2)

                idle_delta = idle_2 - idle_1
                total_delta = total_2 - total_1
                cpu_usage = round((1 - idle_delta / total_delta) * 100, 2)
                load['cpu_usage'] = f'{cpu_usage}%'
            except FileNotFoundError:
                # Windows 환경: PowerShell 사용
                try:
                    result = os.popen(
                        'powershell -command "'
                        '(Get-CimInstance Win32_Processor).LoadPercentage'
                        '"'
                    ).read().strip()
                    if result.isdigit():
                        load['cpu_usage'] = f'{result}%'
                    else:
                        load['cpu_usage'] = 'Unknown'
                except Exception:
                    load['cpu_usage'] = 'Unknown'

        if self.settings.get('memory_usage', True):
            # 메모리 사용량 계산
            try:
                # Linux 환경: /proc/meminfo 사용
                mem_info = {}
                with open('/proc/meminfo', 'r') as f:
                    for line in f:
                        parts = line.split()
                        key = parts[0].rstrip(':')
                        value = int(parts[1])
                        mem_info[key] = value

                total = mem_info.get('MemTotal', 1)
                available = mem_info.get('MemAvailable', 0)
                used_percent = round((1 - available / total) * 100, 2)
                load['memory_usage'] = f'{used_percent}%'
            except FileNotFoundError:
                # Windows 환경: PowerShell 사용
                try:
                    # 전체 메모리 (bytes)
                    result_total = os.popen(
                        'powershell -command "'
                        '(Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory'
                        '"'
                    ).read().strip()
                    # 사용 가능한 메모리 (KB)
                    result_free = os.popen(
                        'powershell -command "'
                        '(Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory'
                        '"'
                    ).read().strip()

                    if result_total.isdigit() and result_free.isdigit():
                        total_bytes = int(result_total)
                        free_kb = int(result_free)
                        total_kb = total_bytes / 1024
                        used_percent = round((1 - free_kb / total_kb) * 100, 2)
                        load['memory_usage'] = f'{used_percent}%'
                    else:
                        load['memory_usage'] = 'Unknown'
                except Exception:
                    load['memory_usage'] = 'Unknown'

        # JSON 형식으로 출력
        print(json.dumps(load, indent=4, ensure_ascii=False))
        return load

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


# MissionComputer 클래스를 runComputer라는 이름으로 인스턴스화
runComputer = MissionComputer()

# 시스템 정보 출력
runComputer.get_mission_computer_info()

# 시스템 부하 정보 출력
runComputer.get_mission_computer_load()
