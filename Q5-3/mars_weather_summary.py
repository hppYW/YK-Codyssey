import csv
import os
import mysql.connector


class MySqlHelper:
    def __init__(self, host='localhost', user='root', password='', database=None, port=3306):
        # MySQL 연결 정보 저장
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port
        self.connection = None

    def connect(self):
        # MySQL 서버에 연결
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port,
            )
            print('MySQL 연결 성공')
            return True
        except mysql.connector.Error as e:
            print(f'MySQL 연결 실패: {e}')
            return False

    def disconnect(self):
        # 연결 종료
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print('MySQL 연결 종료')

    def execute_query(self, query, params=None):
        # INSERT, UPDATE, DELETE 등 실행
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            self.connection.commit()
            affected = cursor.rowcount
            cursor.close()
            return affected
        except mysql.connector.Error as e:
            print(f'쿼리 실행 오류: {e}')
            return -1

    def execute_many(self, query, data_list):
        # 여러 건의 데이터를 한번에 실행
        try:
            cursor = self.connection.cursor()
            cursor.executemany(query, data_list)
            self.connection.commit()
            affected = cursor.rowcount
            cursor.close()
            return affected
        except mysql.connector.Error as e:
            print(f'쿼리 실행 오류: {e}')
            return -1

    def fetch_all(self, query, params=None):
        # SELECT 결과를 전부 반환
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            cursor.close()
            return columns, rows
        except mysql.connector.Error as e:
            print(f'조회 오류: {e}')
            return None, None

    def fetch_one(self, query, params=None):
        # SELECT 결과를 한 건 반환
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            row = cursor.fetchone()
            columns = [desc[0] for desc in cursor.description]
            cursor.close()
            return columns, row
        except mysql.connector.Error as e:
            print(f'조회 오류: {e}')
            return None, None

    def create_database(self, db_name):
        # 데이터베이스 생성
        query = f'CREATE DATABASE IF NOT EXISTS {db_name}'
        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            cursor.close()
            print(f'데이터베이스 생성 완료: {db_name}')
            return True
        except mysql.connector.Error as e:
            print(f'데이터베이스 생성 오류: {e}')
            return False

    def use_database(self, db_name):
        # 사용할 데이터베이스 변경
        try:
            self.connection.database = db_name
            self.database = db_name
            print(f'데이터베이스 선택: {db_name}')
            return True
        except mysql.connector.Error as e:
            print(f'데이터베이스 선택 오류: {e}')
            return False


def create_table(helper):
    # mars_weather 테이블 생성
    query = '''
        CREATE TABLE IF NOT EXISTS mars_weather (
            weather_id INT AUTO_INCREMENT PRIMARY KEY,
            mars_date DATETIME NOT NULL,
            temp INT,
            storm INT
        )
    '''
    result = helper.execute_query(query)
    if result != -1:
        print('mars_weather 테이블 생성 완료')
    return result


def read_csv(file_path):
    # CSV 파일을 읽어서 내용 확인 및 반환
    if not os.path.exists(file_path):
        print(f'파일을 찾을 수 없습니다: {file_path}')
        return []

    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)

    # CSV 내용 확인 출력
    print(f'\n===== CSV 파일 내용 확인 =====')
    print(f'총 {len(data)}건의 데이터')
    if data:
        print(f'컬럼: {list(data[0].keys())}')
        print(f'첫 번째 데이터: {data[0]}')
        print(f'마지막 데이터: {data[-1]}')
    print(f'==============================\n')

    return data


def insert_data(helper, data):
    # CSV 데이터를 mars_weather 테이블에 INSERT
    insert_query = '''
        INSERT INTO mars_weather (weather_id, mars_date, temp, storm)
        VALUES (%s, %s, %s, %s)
    '''

    inserted = 0
    for row in data:
        weather_id = int(row['weather_id'])
        mars_date = row['mars_date']
        temp = int(float(row['temp']))
        # CSV 헤더가 'stom'으로 되어 있음
        storm = int(row.get('stom', row.get('storm', 0)))

        result = helper.execute_query(
            insert_query,
            (weather_id, mars_date, temp, storm)
        )
        if result != -1:
            inserted += 1

    print(f'데이터 입력 완료: {inserted}/{len(data)}건')
    return inserted


def main():
    # MySQL 연결 설정 (환경에 맞게 수정)
    db_name = 'mars_mission'

    helper = MySqlHelper(
        host='localhost',
        user='root',
        password='',
        port=3306,
    )

    # MySQL 연결
    if not helper.connect():
        return

    # 데이터베이스 생성 및 선택
    helper.create_database(db_name)
    helper.use_database(db_name)

    # 테이블 생성
    create_table(helper)

    # CSV 파일 읽기
    csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mars_weathers_data.csv')
    data = read_csv(csv_path)

    if not data:
        helper.disconnect()
        return

    # 데이터 삽입
    insert_data(helper, data)

    # 삽입 결과 확인
    columns, rows = helper.fetch_all('SELECT COUNT(*) AS total FROM mars_weather')
    if rows:
        print(f'\n테이블 내 총 데이터: {rows[0][0]}건')

    # 샘플 데이터 조회
    columns, rows = helper.fetch_all('SELECT * FROM mars_weather LIMIT 5')
    if rows:
        print(f'\n===== 샘플 데이터 (상위 5건) =====')
        print(f'컬럼: {columns}')
        for row in rows:
            print(f'  {row}')
        print(f'===================================\n')

    # 연결 종료
    helper.disconnect()


if __name__ == '__main__':
    main()