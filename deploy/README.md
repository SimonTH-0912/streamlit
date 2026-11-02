# DataLens

CSV 파일을 업로드해 데이터 개요, 품질, 필터 결과, 그래프, 상관관계를 확인하는 Streamlit 앱입니다.

## 실행 방법

```powershell
cd deploy
python -m pip install -r requirements.txt
python -m streamlit run my_csv_reader.py
```

브라우저가 자동으로 열리지 않으면 터미널에 표시된 `Local URL`을 여세요.

CSV 파일이 없어도 사이드바의 **샘플 데이터로 시작**을 선택해 기능을 확인할 수 있습니다. 샘플은 실제 매출이 아닌 가상 데이터입니다. 파일을 업로드하면 업로드한 파일이 사용됩니다.

## 주요 기능

- UTF-8, CP949, EUC-KR 인코딩 자동 처리
- 쉼표, 세미콜론, 탭, 파이프 구분자 지원
- 숫자 범위 및 범주형 값 필터
- 데이터 품질과 기술 통계
- 막대, 선, 영역, 산점도
- 숫자형 열 상관관계
- 필터 결과 CSV 다운로드
