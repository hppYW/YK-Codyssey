import zipfile
import zlib
import time


def _make_crc_table():
    # CRC-32 테이블 생성
    table = []
    for i in range(256):
        crc = i
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ 0xEDB88320
            else:
                crc >>= 1
        table.append(crc)
    return table


CRC_TABLE = _make_crc_table()


# 키 값 갱신
def _update_keys(key0, key1, key2, byte):
    key0 = (key0 >> 8) ^ CRC_TABLE[(key0 ^ byte) & 0xFF]
    key1 = ((key1 + (key0 & 0xFF)) * 134775813 + 1) & 0xFFFFFFFF # 선형 합동 생성기 패턴
    key2 = (key2 >> 8) ^ CRC_TABLE[(key2 ^ ((key1 >> 24) & 0xFF)) & 0xFF]
    return key0, key1, key2


# XOR용 바이트 만들기
def _decrypt_byte(key2):
    temp = (key2 | 2) & 0xFFFF
    return ((temp * (temp ^ 1)) >> 8) & 0xFF


# 암호 복호화
def crack_password(pwd_bytes, enc_header, enc_body, check_crc, check_time, expected_crc):
    key0, key1, key2 = 305419896, 591751049, 878082192

    for c in pwd_bytes:
        key0, key1, key2 = _update_keys(key0, key1, key2, c)

    for i in range(12):
        db = _decrypt_byte(key2)  # key2로 XOR용 바이트 생성
        plain = enc_header[i] ^ db # 헤더 i번쨰 바이트 복호화
        key0, key1, key2 = _update_keys(key0, key1, key2, plain) # 키 갱신

        if i == 11:  # 12번째(마지막) 바이트일 때
            if plain != check_crc and plain != check_time:
                return None

    decrypted_body = bytearray(len(enc_body)) # 결과 담을 빈 배열
    for i in range(len(enc_body)):
        db = _decrypt_byte(key2) # XOR용 바이트 생성 
        decrypted_body[i] = enc_body[i] ^ db # 본문 바이트 복호화
        key0, key1, key2 = _update_keys(key0, key1, key2, decrypted_body[i]) # 키 갱신

    try: # 최종 검증
        decompressed = zlib.decompress(bytes(decrypted_body), -15) # 복호환된 데이터를 압축 해제(-15는 raw deflate 형식 의미)
        if (zlib.crc32(decompressed) & 0xFFFFFFFF) == expected_crc: # 압축 해제된 원본의 CRC-32 계산
            return decompressed # 양수로 만들기
    except Exception:
        pass

    return None


# zip 파일 정보 읽기
def _read_zip_info(zip_path):
    zf = zipfile.ZipFile(zip_path)
    info = zf.infolist()[0]
    expected_crc = info.CRC

    # 체크 바이트 2개 생성
    raw_time = (info.date_time[3] << 11) | (info.date_time[4] << 5) | (info.date_time[5] // 2)
    check_byte_time = (raw_time >> 8) & 0xFF
    check_byte_crc = (expected_crc >> 24) & 0xFF

    # 암호화된 데이터 직접 읽기
    with open(zip_path, 'rb') as f:
        f.seek(info.header_offset) 
        local_hdr = f.read(30)
        fname_len = local_hdr[26] | (local_hdr[27] << 8)
        extra_len = local_hdr[28] | (local_hdr[29] << 8)
        f.read(fname_len + extra_len)
        enc_data = f.read(info.compress_size) # extractall()을 안 씀 raw 데이터를 가져옴 -> 직접 복호화

    zf.close()
    return enc_data[:12], enc_data[12:], check_byte_crc, check_byte_time, expected_crc


def unlock_zip():
    zip_path = 'C:/GitHub/YK-Codyssey/Q1-2/emergency_storage_key.zip'
    password_file = 'password.txt'

    enc_header, enc_body, check_crc, check_time, expected_crc = _read_zip_info(zip_path)

    characters = b'0123456789abcdefghijklmnopqrstuvwxyz'
    char_count = len(characters)
    password_length = 6
    total = char_count ** password_length

    print(f'시작: {time.strftime("%Y-%m-%d %H:%M:%S")}')
    print(f'총 시도 횟수: {total:,}개')
    print(f'체크 바이트 - 시간: {hex(check_time)}, CRC: {hex(check_crc)}')
    print(f'목표 CRC: {hex(expected_crc)}')
    print('-' * 50)

    # 초기 상태
    indices = [0] * password_length
    start_time = time.time()
    found_password = None

    for attempt in range(total):
        pwd_bytes = bytes([characters[idx] for idx in indices])

        result = crack_password(
            pwd_bytes, enc_header, enc_body,
            check_crc, check_time, expected_crc
        )

        if result is not None:
            found_password = pwd_bytes.decode()
            print(f'비밀번호 발견: {found_password}')
            print(f'내용: {result}')
            break

        if (attempt + 1) % 10_000_000 == 0:
            elapsed = time.time() - start_time
            speed = (attempt + 1) / elapsed if elapsed > 0 else 0
            print(f'{attempt + 1:>12,}회 | {pwd_bytes.decode()} | '
                  f'{elapsed:,.0f}초 | {speed:,.0f}/초')

        pos = password_length - 1
        while pos >= 0:
            indices[pos] += 1
            if indices[pos] < char_count:
                break
            indices[pos] = 0
            pos -= 1

    elapsed = time.time() - start_time
    print('-' * 50)

    if found_password:
        print(f'성공! 비밀번호: {found_password}')
        print(f'소요 시간: {elapsed:,.2f}초')
        with open(password_file, 'w') as f:
            f.write(found_password)
    else:
        print(f'실패. {total:,}개 모두 시도.')
        print(f'소요 시간: {elapsed:,.2f}초')

    return found_password


if __name__ == '__main__':
    unlock_zip()
