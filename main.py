print('Hello Mars')

try:
    with open('mission_computer_main.log', 'r', encoding='utf-8') as f:
        lines = f.readlines()

    print('=== 정순 출력 ===')
    print(''.join(lines))

    print('=== 역순 출력 ===')
    print(''.join(reversed(lines)))

except FileNotFoundError:
    print('Error: mission_computer_main.log 파일을 찾을 수 없습니다.')
except PermissionError:
    print('Error: 파일에 접근할 권한이 없습니다.')
except UnicodeDecodeError:
    print('Error: 파일 인코딩을 읽을 수 없습니다.')
except OSError as e:
    print(f'Error: 파일 읽기 중 오류가 발생했습니다. {e}')
