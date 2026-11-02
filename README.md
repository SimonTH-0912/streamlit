# DataLens — CSV 데이터 분석 대시보드

CSV 파일을 업로드해 데이터의 구조와 품질을 살펴보고, 필터와 그래프를 이용해 탐색하는 Streamlit 앱입니다.

[라이브 데모](https://mycsvreader.streamlit.app/) · [상세 실행 안내](deploy/README.md)

## 주요 기능

- UTF-8·CP949·EUC-KR 인코딩 시도와 구분자 선택
- 숫자형·범주형 필터 및 결과 CSV 다운로드
- 결측값·중복 행·기술 통계 확인
- 막대·선·영역·산점도와 숫자형 열의 상관관계
- 파일 없이 살펴볼 수 있는 가상 샘플 데이터

## 실행 방법

```powershell
git clone https://github.com/SimonTH-0912/streamlit.git
cd streamlit/deploy
python -m pip install -r requirements.txt
python -m streamlit run my_csv_reader.py
```

데모의 사이드바에서 CSV를 업로드하거나 샘플 데이터를 선택할 수 있습니다. 앱이 비활성 상태였다면 처음 실행할 때 준비 시간이 필요할 수 있습니다.

## 해석 시 유의점

결과는 입력한 데이터의 품질에 영향을 받습니다. 상관관계는 인과관계를 의미하지 않습니다.
