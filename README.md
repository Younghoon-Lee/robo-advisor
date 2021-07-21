# robo-advisor

# QUICK START

(python version 3.8.8)

1. $ pip3 install -r requirements.txt

2. $ python3 src/stock_data_collecotr.py (하루에 한번/stock data를 업데이트 하기위함)

3. main.py 실행

- 유저 투자자성향 및 금액 설정
- backTest 는 False 값으로 설정
- backTest = True 는 오직 RATB 현장심사와 사전심사를 위한 용도 임. 실제 운용 단계에서는 필요 없음

---

# DESCRIPTION

1. universe.csv

- 투자 유니버스(투자 유니버스 내에 있는 자산 종목만 투자할 수 있음)

2. src 폴더

- stock data update 용도
- stock_data_collector 모듈을 통해 krx 로부터 stock data를 스크래핑 하여 data 폴더에 저장

3. roboadvisor

- optimizer : optimizer 모듈을 통해 최적의 포트폴리오 가중치를 산출
- rebalancer : optimizer를 통해 산출된 가중치를 바탕으로 매수, 매도 수량 산출

4. app (현장심사 용도)

- Flask 기반으로 작성된 robo-adviosr-app demo 버젼
