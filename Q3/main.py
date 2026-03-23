import csv
import pickle

def main():
    try:
        # csv 파일 읽고 csv.reader로 출력 / 빈 리스트를 만들어서 append 추가
        with open('Mars_Base_Inventory_List.csv', 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            inventory_list = []
            for row in reader:
                print(row)
                inventory_list.append(row)

        print("-" * 50)

        # 리스트문에 0번째는 header로 달고 나머지는 data / sorted문에 x[4](인화성)을 높은 순으로 정렬
        header = inventory_list[0]
        data = inventory_list[1:]
        # x는 익명 함수 - 각 행(row)
        sorted_list = sorted(data, key=lambda x: float(x[4]), reverse=True)

        print(header)
        for row in sorted_list:
            print(row)

        print("-" * 50)

        # row[4](인화성)이 0.7보다 높은 목록만 danger_list에 저장
        danger_list = [row for row in sorted_list if float(row[4]) >= 0.7]

        print(header)
        for row in danger_list:
            print(row)

        # pickle.dump 파이썬 객체 -> 이진 데이터로 변환 후 저장
        with open('Mars_Base_Inventory_List.bin', 'wb') as f:
            pickle.dump(sorted_list, f)

        # 0.7 이상인 인화성 목록 csv 저장 / newline으로 줄바꿈 방지
        with open('Mar_Base_Inventory_danger.csv', 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(danger_list)

    except FileNotFoundError as e:
        print(f'파일을 찾을 수 없습니다: {e}')
    except ValueError as e:
        print(f'데이터 변환 오류: {e}')
    except Exception as e:
        print(f'오류 발생: {e}')

def read_bin():
    try:
        # bin 파일 출력
        with open('Mars_Base_Inventory_List.bin', 'rb') as f:
            data = pickle.load(f)
        for row in data:
            print(row)
    except FileNotFoundError as e:
        print(f'파일을 찾을 수 없습니다: {e}')
    except Exception as e:
        print(f'오류 발생: {e}')

if __name__ == '__main__':
    main()
    print("-" * 50)
    read_bin()
