# 카이사르 암호 해독 프로그램


def caesar_cipher_decode(target_text):
    # 보너스: 영어 단어 사전
    dictionary = [
        'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'it',
        'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at', 'this',
        'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she', 'or',
        'will', 'my', 'one', 'all', 'would', 'there', 'their', 'what',
        'so', 'up', 'out', 'if', 'about', 'who', 'get', 'which', 'go', 'me',
        'when', 'make', 'can', 'like', 'time', 'no', 'just', 'him', 'know',
        'take', 'people', 'into', 'year', 'your', 'good', 'some', 'could',
        'them', 'see', 'other', 'than', 'then', 'now', 'look', 'only',
        'come', 'its', 'over', 'think', 'also', 'back', 'after', 'use',
        'two', 'how', 'our', 'work', 'first', 'well', 'way', 'even', 'new',
        'want', 'because', 'any', 'these', 'give', 'day', 'most', 'us',
        'life', 'was', 'found', 'mars', 'mission', 'space', 'planet',
        'launch', 'code', 'secret', 'oxygen', 'tank', 'houston', 'problem'
    ]

    found_shift = None

    # 1~26 자리수로 해독 시도
    for shift in range(1, 27):
        decoded = ''
        for char in target_text:
            if char.isalpha():
                # 대문자/소문자 구분하여 시프트
                base = ord('A') if char.isupper() else ord('a')
                decoded += chr((ord(char) - base - shift) % 26 + base)
            else:
                # 알파벳이 아닌 문자는 그대로 유지
                decoded += char

        print(f'자리수 {shift:2d}: {decoded}')

        # 보너스: 사전 단어 매칭으로 자동 감지
        decoded_words = decoded.lower().split()
        match_count = sum(1 for word in decoded_words if word in dictionary)

        if match_count >= 2:
            found_shift = shift
            print(f'\n>>> 자리수 {shift}에서 사전 단어 {match_count}개 발견! <<<')
            print(f'해독 결과: {decoded}')
            break

    # 자동 감지 실패 시 수동 입력
    if found_shift is None:
        print('\n사전에서 자동 감지하지 못했습니다.')
        shift_input = input('해독된 자리수 번호를 입력하세요: ')
        found_shift = int(shift_input)

        # 입력된 자리수로 해독
        decoded = ''
        for char in target_text:
            if char.isalpha():
                base = ord('A') if char.isupper() else ord('a')
                decoded += chr((ord(char) - base - found_shift) % 26 + base)
            else:
                decoded += char
    else:
        # 사전에서 찾은 자리수로 해독 (이미 위에서 decoded 완성됨)
        pass

    return decoded


# password.txt 파일 읽기
with open('password.txt', 'r') as file:
    encrypted_text = file.read().strip()

print(f'암호문: {encrypted_text}')
print('=' * 40)

# 카이사르 암호 해독
result = caesar_cipher_decode(encrypted_text)

# 결과를 result.txt로 저장
with open('result.txt', 'w') as file:
    file.write(result)

print(f'\n결과가 result.txt에 저장되었습니다: {result}')
