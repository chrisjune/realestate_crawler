import urllib.parse
from datetime import datetime
from logging import getLogger
from xml.etree import cElementTree as ElementTree

import config
import psycopg2
import requests
from query import (CREATE_CITY_TABLE, CREATE_SCHEMA, CREATE_TRANSACTION_TABLE,
                   GRANT_DB_TO_USER, INSERT_CITY_DATA)
from utils import XmlDictConfig, XmlListConfig


class InitSetting:
    """
    DB에 테이블을 생성 및 도시정보 저장
    """
    def __init__(self):
        host = config.HOST
        port = config.PORT
        db = config.DB
        user = config.USER
        password = config.PASSWORD
        self.conn = psycopg2.connect(host=host, port=port, database=db, user=user, password=password)

    def refresh_connection(self):
        """
        connection을 갱신
        """
        self.__init__()

    def create_init_data(self):
        """
        초기 테이블 생성과 도시정보를 생성
        """
        with self.conn.cursor() as cursor:
            cursor.execute(GRANT_DB_TO_USER % (config.DB, config.USER))
            cursor.execute(CREATE_SCHEMA)
            cursor.execute(CREATE_CITY_TABLE)
            cursor.execute(INSERT_CITY_DATA)
            cursor.execute(CREATE_TRANSACTION_TABLE)
            self.conn.commit()

    def get_city_code(self):
        """
        도시정보를 조회
        """
        with self.conn.cursor() as cursor:
            cursor.execute("select * from apartment.city;")
            result = cursor.fetchall()
            return result

    def get_query_date(self):
        """
        실거래가 최초 기준인 2006년부터 조회할 현재시간을 반환
        """
        date_list = []
        now = datetime.now()
        start_year = 2006
        end_year = now.year
        end_month = now.month

        for year in range(start_year, end_year+1):
            for month in range(1, 12+1):
                if year == end_year and end_month < month:
                    break
                date_list.append(str(year)+str(month).zfill(2))
        return date_list

    def runner(self, date_code, city_list):
        """
        API를 호출하여 적재
        """
        for city in city_list:
            city_code = str(city[0])
            print("START", date_code, city)
            url = 'http://openapi.molit.go.kr/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcAptTradeDev'
            queryParams = '?' + urllib.parse.urlencode(
                {
                    'ServiceKey':config.SECRETKEY,
                    'pageNo':'1',
                    'numOfRows':'1000000',
                    'LAWD_CD':city_code,
                    'DEAL_YMD': date_code
                }
            )
            url = url + queryParams
            response_body = requests.get(url)
            xml = response_body.text

            root = ElementTree.XML(xml)
            xmldict = XmlDictConfig(root)

            price_data = xmldict.get('body','').get('items', '').get('item', [])

            for data in price_data:
                dic = {
                    'price': int(data.get('거래금액','').replace(' ', '').replace(',','')),
                    'built_year': int(data.get('건축년도')),
                    'road_name': data.get('도로명'),
                    'road_building_main_code': data.get('도로명건물본번호코드'),
                    'road_building_sub_code': data.get('도로명건물부번호코드'),
                    'road_city_code': data.get('도로명시군구코드'),
                    'road_serial_code':data.get('도로명일련번호코드'),
                    'road_basement_code':data.get('도로명지상지하코드'),
                    'road_code':data.get('도로명코드'),
                    'region_name':data.get('법정동'),
                    'region_main_code':data.get('법정동본번코드'),
                    'region_sub_code':data.get('법정동부번코드'),
                    'region_city_code':data.get('법정동시군구코드'),
                    'region_city2_code':data.get('법정동읍면동코드'),
                    'region_zip_code':data.get('법정동지번코드'),
                    'apart_name':data.get('아파트'),
                    'year':data.get('년'),
                    'month':data.get('월'),
                    'day':data.get('일'),
                    'serial_no':data.get('일련번호'),
                    'size':float(data.get('전용면적')),
                    'zip_code':data.get('지번'),
                    'city_code':data.get('지역코드'),
                    'floor':int(data.get('층'))
                }

                with self.conn.cursor() as cur:
                    placeholders = ', '.join(['%s'] * len(dic))
                    columns = ', '.join(dic.keys())
                    table = 'apartment.transaction'
                    sql = "INSERT INTO %s ( %s ) VALUES ( %s )" % (table, columns, placeholders)
                    cur.execute(sql, list(dic.values()))
                    self.conn.commit()


if __name__ == '__main__':
    try:
        logger = getLogger('crawler logger')
        logger.warning('CRAWLER START')

        crawler = InitSetting()
        crawler.create_init_data()

        date_list = crawler.get_query_date()
        city_list = crawler.get_city_code()

        for index, date_code in enumerate(date_list):
            crawler.refresh_connection()
            crawler.runner(date_code, city_list)
            logger.warning((date_code, 'done'))
    except AttributeError as e:
        logger.error('CRAWLER STOPPED -%s', e)
    else:
        logger.warning('CRAWLER FINISHED')
