import json
import os
import platform
import time


class MissionComputer:
    def _get_memory_size(self):
        # OS별 전체 메모리 크기를 GB 문자열로 반환
        try:
            with open('/proc/meminfo', 'r') as f:
                for line in f:
                    if line.startswith('MemTotal'):
                        mem_kb = int(line.split()[1])
                        return f'{round(mem_kb / 1024 / 1024, 2)} GB'
        except FileNotFoundError:
            pass

        # Windows 환경
        result = os.popen(
            'powershell -command "'
            '(Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory"'
        ).read().strip()
        if result.isdigit():
            return f'{round(int(result) / 1024 ** 3, 2)} GB'
        return 'Unknown'

    def get_mission_computer_info(self):
        # 미션 컴퓨터의 시스템 정보를 JSON 형식으로 출력
        info = {
            'os': platform.system(),
            'os_version': platform.version(),
            'cpu_type': platform.processor(),
            'cpu_cores': os.cpu_count(),
            'memory_size': self._get_memory_size(),
        }
        print(json.dumps(info, indent=4, ensure_ascii=False))
        return info

    def _get_cpu_usage(self):
        # OS별 CPU 사용률을 반환
        try:
            with open('/proc/stat', 'r') as f:
                line1 = f.readline()
            times1 = [int(x) for x in line1.split()[1:]]

            time.sleep(1)

            with open('/proc/stat', 'r') as f:
                line2 = f.readline()
            times2 = [int(x) for x in line2.split()[1:]]

            idle_d = times2[3] - times1[3]
            total_d = sum(times2) - sum(times1)
            return f'{round((1 - idle_d / total_d) * 100, 2)}%'
        except FileNotFoundError:
            pass

        # Windows 환경
        result = os.popen(
            'powershell -command "'
            '(Get-CimInstance Win32_Processor).LoadPercentage"'
        ).read().strip()
        return f'{result}%' if result.isdigit() else 'Unknown'

    def _get_memory_usage(self):
        # OS별 메모리 사용률을 반환
        try:
            mem = {}
            with open('/proc/meminfo', 'r') as f:
                for line in f:
                    parts = line.split()
                    mem[parts[0].rstrip(':')] = int(parts[1])
            used = round((1 - mem['MemAvailable'] / mem['MemTotal']) * 100, 2)
            return f'{used}%'
        except FileNotFoundError:
            pass

        # Windows 환경
        total = os.popen(
            'powershell -command "'
            '(Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory"'
        ).read().strip()
        free = os.popen(
            'powershell -command "'
            '(Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory"'
        ).read().strip()
        if total.isdigit() and free.isdigit():
            used = round((1 - int(free) / (int(total) / 1024)) * 100, 2)
            return f'{used}%'
        return 'Unknown'

    def get_mission_computer_load(self):
        # 미션 컴퓨터의 실시간 부하를 JSON 형식으로 출력
        load = {
            'cpu_usage': self._get_cpu_usage(),
            'memory_usage': self._get_memory_usage(),
        }
        print(json.dumps(load, indent=4, ensure_ascii=False))
        return load


# MissionComputer 클래스를 runComputer라는 이름으로 인스턴스화
runComputer = MissionComputer()

# 시스템 정보 출력
runComputer.get_mission_computer_info()

# 시스템 부하 정보 출력
runComputer.get_mission_computer_load()
