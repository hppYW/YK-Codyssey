import sounddevice as sd
import speech_recognition as sr
import wave
import struct
import os
import datetime
import csv


class AudioRecorder:
    def __init__(self):
        # 오디오 설정
        self.channels = 1
        self.rate = 44100

        # 녹음 상태 관리
        self.is_recording = False
        self.frames = []

        # records 폴더 경로 설정
        self.records_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'records')
        os.makedirs(self.records_dir, exist_ok=True)

    def list_microphones(self):
        # 시스템에서 사용 가능한 마이크 목록 출력
        print('\n===== 사용 가능한 마이크 목록 =====')
        devices = sd.query_devices()
        mic_list = []

        for i, device in enumerate(devices):
            if device['max_input_channels'] > 0:
                mic_list.append((i, device))
                print(f'  [{i}] {device["name"]} (입력 채널: {device["max_input_channels"]})')

        if not mic_list:
            print('  사용 가능한 마이크가 없습니다.')
        print('==================================\n')
        return mic_list

    def start_recording(self, device_index=None):
        # 녹음 시작
        if self.is_recording:
            print('이미 녹음 중입니다.')
            return

        self.frames = []
        self.is_recording = True

        # 콜백 함수: 오디오 데이터를 프레임에 저장
        def callback(indata, frame_count, time_info, status):
            if self.is_recording:
                self.frames.append(indata.copy())

        try:
            self.stream = sd.InputStream(
                samplerate=self.rate,
                channels=self.channels,
                device=device_index,
                callback=callback,
            )
            self.stream.start()
            print('녹음을 시작합니다. 중지하려면 Enter를 누르세요.')
        except Exception as e:
            print(f'마이크를 열 수 없습니다: {e}')
            self.is_recording = False

    def stop_recording(self):
        # 녹음 중지 및 파일 저장
        if not self.is_recording:
            print('녹음 중이 아닙니다.')
            return None

        self.is_recording = False
        self.stream.stop()
        self.stream.close()

        if not self.frames:
            print('녹음된 데이터가 없습니다.')
            return None

        # 파일명 생성 (년월일-시간분초)
        now = datetime.datetime.now()
        filename = now.strftime('%Y%m%d-%H%M%S') + '.wav'
        filepath = os.path.join(self.records_dir, filename)

        # 녹음 데이터를 16비트 정수로 변환하여 WAV 저장
        audio_data = []
        for frame in self.frames:
            for sample in frame:
                value = int(sample[0] * 32767)
                value = max(-32768, min(32767, value))
                audio_data.append(value)

        wf = wave.open(filepath, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(2)
        wf.setframerate(self.rate)
        wf.writeframes(struct.pack(f'<{len(audio_data)}h', *audio_data))
        wf.close()

        # 녹음 시간 계산
        duration = len(audio_data) / self.rate
        print(f'녹음 완료: {filename} ({duration:.1f}초)')
        return filepath

    def list_records(self, start_date=None, end_date=None):
        # 녹음 파일 목록 조회 (날짜 범위 필터링 가능)
        if not os.path.exists(self.records_dir):
            print('records 폴더가 존재하지 않습니다.')
            return []

        files = sorted(os.listdir(self.records_dir))
        wav_files = [f for f in files if f.endswith('.wav')]

        if not wav_files:
            print('저장된 녹음 파일이 없습니다.')
            return []

        # 날짜 범위 필터링
        if start_date or end_date:
            filtered = []
            for f in wav_files:
                try:
                    date_str = f.replace('.wav', '')
                    file_date = datetime.datetime.strptime(date_str, '%Y%m%d-%H%M%S')
                except ValueError:
                    continue

                if start_date and file_date < start_date:
                    continue
                if end_date and file_date > end_date:
                    continue
                filtered.append(f)
            wav_files = filtered

        # 결과 출력
        if not wav_files:
            print('해당 날짜 범위에 녹음 파일이 없습니다.')
            return []

        print('\n===== 녹음 파일 목록 =====')
        for f in wav_files:
            filepath = os.path.join(self.records_dir, f)
            size = os.path.getsize(filepath)
            size_kb = size / 1024
            print(f'  {f} ({size_kb:.1f} KB)')
        print(f'  총 {len(wav_files)}개 파일')
        print('==========================\n')
        return wav_files

    def close(self):
        # 리소스 해제
        if self.is_recording:
            self.stop_recording()


class SpeechToText:
    def __init__(self, records_dir=None):
        # STT 엔진 초기화
        self.recognizer = sr.Recognizer()

        # records 폴더 경로 설정
        if records_dir:
            self.records_dir = records_dir
        else:
            self.records_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'records')

    def get_audio_files(self):
        # records 폴더에서 WAV 파일 목록 반환
        if not os.path.exists(self.records_dir):
            print('records 폴더가 존재하지 않습니다.')
            return []

        files = sorted(os.listdir(self.records_dir))
        wav_files = [f for f in files if f.endswith('.wav')]

        if not wav_files:
            print('저장된 음성 파일이 없습니다.')
            return []

        print('\n===== 음성 파일 목록 =====')
        for i, f in enumerate(wav_files):
            filepath = os.path.join(self.records_dir, f)
            size_kb = os.path.getsize(filepath) / 1024
            print(f'  [{i + 1}] {f} ({size_kb:.1f} KB)')
        print(f'  총 {len(wav_files)}개 파일')
        print('==========================\n')
        return wav_files

    def transcribe(self, wav_filename):
        # 음성 파일에서 텍스트 추출 (구간별로 분할하여 인식)
        filepath = os.path.join(self.records_dir, wav_filename)

        if not os.path.exists(filepath):
            print(f'파일을 찾을 수 없습니다: {wav_filename}')
            return []

        print(f'음성 인식 중: {wav_filename}')
        results = []

        try:
            with sr.AudioFile(filepath) as source:
                # 전체 오디오 길이 계산
                total_duration = source.DURATION
                # 10초 단위로 분할하여 인식
                chunk_duration = 10
                offset = 0

                while offset < total_duration:
                    remaining = total_duration - offset
                    duration = min(chunk_duration, remaining)

                    audio = self.recognizer.record(source, duration=duration)

                    try:
                        # Google Web Speech API로 한국어 인식
                        text = self.recognizer.recognize_google(audio, language='ko-KR')
                        # 시간 포맷 (MM:SS)
                        minutes = int(offset) // 60
                        seconds = int(offset) % 60
                        time_str = f'{minutes:02d}:{seconds:02d}'
                        results.append((time_str, text))
                        print(f'  [{time_str}] {text}')
                    except sr.UnknownValueError:
                        pass
                    except sr.RequestError as e:
                        print(f'  음성 인식 서비스 오류: {e}')
                        break

                    offset += chunk_duration

        except Exception as e:
            print(f'파일 처리 오류: {e}')
            return []

        if not results:
            print('  인식된 텍스트가 없습니다.')

        return results

    def save_to_csv(self, wav_filename, results):
        # 인식 결과를 CSV 파일로 저장
        csv_filename = wav_filename.replace('.wav', '.csv')
        csv_filepath = os.path.join(self.records_dir, csv_filename)

        with open(csv_filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['시간', '인식된 텍스트'])
            for time_str, text in results:
                writer.writerow([time_str, text])

        print(f'CSV 저장 완료: {csv_filename}')
        return csv_filepath

    def transcribe_and_save(self, wav_filename):
        # 음성 인식 후 CSV로 저장
        results = self.transcribe(wav_filename)
        if results:
            self.save_to_csv(wav_filename, results)
        return results

    def transcribe_all(self):
        # 모든 음성 파일을 인식하고 CSV로 저장
        wav_files = self.get_audio_files()
        if not wav_files:
            return

        for wav_file in wav_files:
            self.transcribe_and_save(wav_file)
            print()

    def search_keyword(self, keyword):
        # 저장된 CSV 파일에서 키워드 검색
        if not os.path.exists(self.records_dir):
            print('records 폴더가 존재하지 않습니다.')
            return

        files = sorted(os.listdir(self.records_dir))
        csv_files = [f for f in files if f.endswith('.csv')]

        if not csv_files:
            print('저장된 CSV 파일이 없습니다. 먼저 음성 인식을 실행하세요.')
            return

        print(f'\n===== 키워드 검색: "{keyword}" =====')
        found = False

        for csv_file in csv_files:
            csv_filepath = os.path.join(self.records_dir, csv_file)
            file_results = []

            with open(csv_filepath, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                header = next(reader, None)
                for row in reader:
                    if len(row) >= 2 and keyword in row[1]:
                        file_results.append(row)

            if file_results:
                found = True
                print(f'\n  [{csv_file}]')
                for row in file_results:
                    print(f'    [{row[0]}] {row[1]}')

        if not found:
            print(f'  "{keyword}"을(를) 포함하는 결과가 없습니다.')
        print('====================================\n')


def parse_date(date_str):
    # 날짜 문자열 파싱
    date_str = date_str.strip()
    for fmt in ('%Y%m%d', '%Y-%m-%d'):
        try:
            return datetime.datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    return None


def main():
    recorder = AudioRecorder()
    stt = SpeechToText(recorder.records_dir)

    # 마이크 목록 표시
    mics = recorder.list_microphones()
    if not mics:
        print('마이크를 찾을 수 없습니다.')

    while True:
        print('메뉴를 선택하세요:')
        print('  1. 녹음 시작')
        print('  2. 녹음 파일 목록 보기')
        print('  3. 날짜 범위로 녹음 파일 검색')
        print('  4. 마이크 목록 보기')
        print('  5. 음성 파일 텍스트 변환 (STT)')
        print('  6. 전체 음성 파일 텍스트 변환')
        print('  7. CSV 키워드 검색')
        print('  q. 종료')

        choice = input('>> ').strip()

        if choice == '1':
            # 마이크 선택
            device_input = input('마이크 번호를 입력하세요 (기본값: 기본 마이크): ').strip()
            device_index = None
            if device_input:
                try:
                    device_index = int(device_input)
                except ValueError:
                    print('잘못된 번호입니다. 기본 마이크를 사용합니다.')

            recorder.start_recording(device_index)
            input()
            recorder.stop_recording()

        elif choice == '2':
            recorder.list_records()

        elif choice == '3':
            # 날짜 범위 입력
            start_input = input('시작 날짜 (YYYYMMDD 또는 YYYY-MM-DD, 비우면 제한 없음): ').strip()
            end_input = input('종료 날짜 (YYYYMMDD 또는 YYYY-MM-DD, 비우면 제한 없음): ').strip()

            start_date = parse_date(start_input) if start_input else None
            end_date = None
            if end_input:
                end_date = parse_date(end_input)
                if end_date:
                    end_date = end_date.replace(hour=23, minute=59, second=59)

            if (start_input and not start_date) or (end_input and not end_date):
                print('날짜 형식이 올바르지 않습니다.')
                continue

            recorder.list_records(start_date, end_date)

        elif choice == '4':
            recorder.list_microphones()

        elif choice == '5':
            # 개별 음성 파일 STT
            wav_files = stt.get_audio_files()
            if wav_files:
                file_input = input('변환할 파일 번호를 입력하세요: ').strip()
                try:
                    idx = int(file_input) - 1
                    if 0 <= idx < len(wav_files):
                        stt.transcribe_and_save(wav_files[idx])
                    else:
                        print('잘못된 번호입니다.')
                except ValueError:
                    print('숫자를 입력하세요.')

        elif choice == '6':
            # 전체 음성 파일 STT
            stt.transcribe_all()

        elif choice == '7':
            # CSV 키워드 검색
            keyword = input('검색할 키워드를 입력하세요: ').strip()
            if keyword:
                stt.search_keyword(keyword)
            else:
                print('키워드를 입력하세요.')

        elif choice.lower() == 'q':
            break

        else:
            print('잘못된 입력입니다.')

    recorder.close()
    print('프로그램을 종료합니다.')


if __name__ == '__main__':
    main()
