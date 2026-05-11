import zipfile
import time


def unlock_zip():
    # ZIP 파일 및 결과 저장 경로
    zip_path = '../emergency_storage_key.zip'
    password_file = 'password.txt'

    # 비밀번호 구성 문자: 숫자 + 소문자 알파벳
    characters = '0123456789abcdefghijklmnopqrstuvwxyz'
    password_length = 6
    total_combinations = len(characters) ** password_length

    # 시작 시간 기록
    start_time = time.time()
    print(f'시작 시간: {time.strftime("%Y-%m-%d %H:%M:%S")}')
    print(f'문자 집합: 숫자(0-9) + 소문자(a-z) = {len(characters)}자')
    print(f'비밀번호 길이: {password_length}자리')
    print(f'총 조합 수: {total_combinations:,}개')
    print('-' * 50)

    try:
        zf = zipfile.ZipFile(zip_path)
    except FileNotFoundError:
        print(f'오류: ZIP 파일을 찾을 수 없습니다 - {zip_path}')
        return

    attempt_count = 0

    # 숫자를 36진법 문자열로 변환하여 모든 조합 순회
    for i in range(total_combinations):
        attempt_count += 1

        # i를 6자리 36진법 문자열로 변환
        password = ''
        num = i
        for _ in range(password_length):
            password = characters[num % len(characters)] + password
            num //= len(characters)

        # 진행 상황 출력 (100만 회마다)
        if attempt_count % 1_000_000 == 0:
            elapsed = time.time() - start_time
            speed = attempt_count / elapsed if elapsed > 0 else 0
            print(f'시도 횟수: {attempt_count:>15,}회 | '
                  f'현재 시도: {password} | '
                  f'경과 시간: {elapsed:,.1f}초 | '
                  f'속도: {speed:,.0f}회/초')

        try:
            zf.extractall(pwd=password.encode())
            # 비밀번호 찾기 성공
            elapsed = time.time() - start_time
            print('-' * 50)
            print(f'비밀번호 찾기 성공!')
            print(f'비밀번호: {password}')
            print(f'총 시도 횟수: {attempt_count:,}회')
            print(f'총 소요 시간: {elapsed:,.2f}초')
            print(f'종료 시간: {time.strftime("%Y-%m-%d %H:%M:%S")}')

            # 비밀번호를 파일로 저장
            with open(password_file, 'w') as f:
                f.write(password)
            print(f'비밀번호가 {password_file}에 저장되었습니다.')

            zf.close()
            return password

        except (RuntimeError, zipfile.BadZipFile):
            pass
        except Exception:
            pass

    # 모든 조합 시도 후 실패
    elapsed = time.time() - start_time
    print('-' * 50)
    print(f'비밀번호를 찾지 못했습니다.')
    print(f'총 시도 횟수: {attempt_count:,}회')
    print(f'총 소요 시간: {elapsed:,.2f}초')
    zf.close()
    return None


if __name__ == '__main__':
    unlock_zip()
