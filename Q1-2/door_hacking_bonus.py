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


def _update_keys(key0, key1, key2, byte):
    key0 = (key0 >> 8) ^ CRC_TABLE[(key0 ^ byte) & 0xFF]
    key1 = ((key1 + (key0 & 0xFF)) * 134775813 + 1) & 0xFFFFFFFF
    key2 = (key2 >> 8) ^ CRC_TABLE[(key2 ^ ((key1 >> 24) & 0xFF)) & 0xFF]
    return key0, key1, key2


def _decrypt_byte(key2):
    temp = (key2 | 2) & 0xFFFF
    return ((temp * (temp ^ 1)) >> 8) & 0xFF


def crack_password(pwd_bytes, enc_header, enc_body, check_crc, check_time, expected_crc):
    key0, key1, key2 = 305419896, 591751049, 878082192

    for c in pwd_bytes:
        key0, key1, key2 = _update_keys(key0, key1, key2, c)

    for i in range(12):
        db = _decrypt_byte(key2)
        plain = enc_header[i] ^ db
        key0, key1, key2 = _update_keys(key0, key1, key2, plain)

        if i == 11:
            if plain != check_crc and plain != check_time:
                return None

    decrypted_body = bytearray(len(enc_body))
    for i in range(len(enc_body)):
        db = _decrypt_byte(key2)
        decrypted_body[i] = enc_body[i] ^ db
        key0, key1, key2 = _update_keys(key0, key1, key2, decrypted_body[i])

    try:
        decompressed = zlib.decompress(bytes(decrypted_body), -15)
        if (zlib.crc32(decompressed) & 0xFFFFFFFF) == expected_crc:
            return decompressed
    except Exception:
        pass

    return None


def _read_zip_info(zip_path):
    zf = zipfile.ZipFile(zip_path)
    info = zf.infolist()[0]
    expected_crc = info.CRC

    raw_time = (info.date_time[3] << 11) | (info.date_time[4] << 5) | (info.date_time[5] // 2)
    check_byte_time = (raw_time >> 8) & 0xFF
    check_byte_crc = (expected_crc >> 24) & 0xFF

    with open(zip_path, 'rb') as f:
        f.seek(info.header_offset)
        local_hdr = f.read(30)
        fname_len = local_hdr[26] | (local_hdr[27] << 8)
        extra_len = local_hdr[28] | (local_hdr[29] << 8)
        f.read(fname_len + extra_len)
        enc_data = f.read(info.compress_size)

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

    # ===== 여기서 시작점 설정 =====
    start_from = 1_340_000_000
    # =============================

    print(f'시작: {time.strftime("%Y-%m-%d %H:%M:%S")}')
    print(f'범위: {start_from:,} ~ {total:,} ({total - start_from:,}개)')
    print(f'체크 바이트 - 시간: {hex(check_time)}, CRC: {hex(check_crc)}')
    print(f'목표 CRC: {hex(expected_crc)}')
    print('-' * 50)

    indices = [0] * password_length
    num = start_from
    for pos in range(password_length - 1, -1, -1):
        indices[pos] = num % char_count
        num //= char_count

    start_time = time.time()
    found_password = None

    for attempt in range(start_from, total):
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
            speed = (attempt + 1 - start_from) / elapsed if elapsed > 0 else 0
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
        print(f'실패. {total - start_from:,}개 모두 시도.')
        print(f'소요 시간: {elapsed:,.2f}초')

    return found_password


if __name__ == '__main__':
    unlock_zip()
