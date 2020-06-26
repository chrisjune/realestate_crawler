# 국토부 실거래가를 한번에 DB에 적재해주는 크롤러
## 활용방법
1. [공공데이터포털](https://data.go.kr/tcs/dss/selectApiDataDetailView.do?publicDataPk=15057511)에서 API 신청
2. 신청 후 즉시사용이 가능하며, 신청완료후 서비스정보 > 일반인증키를 config의 SERVICEKEY에 저장
3. 데이터를 저장할 Postgresql DB 서버를 생성
    - `>>> docker-compose up -d`
4. DB서버가 잘 실행중인지 확인
    - `>>> docker ps --filter name=real_estate_tnx`
5. DB서버가 잘 실행됐다면, requirements.txt의 모듈을 설치
    - `>>> pip3 install -r requirements.txt`
6. 모든 준비가 완료되었고 스크립트를 실행
    - `>>> python3 runner.py`
7. 완료

![크롤링 시작](https://github.com/chrisjune/realestate_crawler/blob/master/img/screenshot_start.png?raw=true)
![크롤링 종료](https://github.com/chrisjune/realestate_crawler/blob/master/img/screenshot_end.png?raw=true)

## FAQ
* DB가 정상적으로 실행되지 않을 때
  - docker 컨테이너를 삭제 후 다시 생성합니다 `>>> docker-compose down; docker-compose up -d`
* 스키마에러 또는 테이블관련 에러가 발생한 경우
  - docker 컨테이너를 삭제하고 postgresql 서버 데이터를 삭제후 다시 스크립트를 실행합니다 
      - `>>> docker-compose down; rm -rf $HOME/docker/volumes/postgres/realestate ; docker-compose up -d`
* 크롤링을 완료 후 데이터만 따로 사용하고 싶은 경우
  - Postgresql DB서버 docker container는 HOST의 `$HOME/docker/volumes/postgres/realestate`에 마운트된 볼륨을 사용하면됩니다.
