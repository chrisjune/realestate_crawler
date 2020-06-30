from runner import InitSetting
import requests, json
from pyproj import Proj, transform
from urllib.parse import urlencode
from config import GEOSECRETKEY
from query import SELECT_TRANSACTION_FOR_LOCATION, INSERT_LOCATION, CREATE_LOCATION_TABLE


class Location:
    """
    아파트 거래내역에서 아파트정보를 조회하고 공공데이터 좌표API를 호출하여 위도경도를 저장
    """
    def to_wsg84(self, x, y):
        """
        공공데이터 좌표API에서 제공하는 UTMK4 좌표계 -> WSG84 좌표계(일반 위도경도)로 변환
        """
        proj_UTMK4 = Proj('+proj=tmerc +lat_0=38 +lon_0=127.5 +k=0.9996 +x_0=1000000 +y_0=2000000 +ellps=GRS80 +units=m +no_defs')
        proj_WSG84 = Proj('epsg:4326')

        if not x or not y:
            return None, None
        return transform(proj_UTMK4, proj_WSG84, x, y)

    def apartment_info(self):
        """
        거래내역에서 아파트의 위치정보를 조회
        """
        results = []
        with conn.cursor () as cursor:
            cursor.execute(SELECT_TRANSACTION_FOR_LOCATION)
            results = cursor.fetchall()
        return results

    def call_juso_api(self, result):
        serial_no = result[0]
        admin_code = result[1]
        road_code = result[2]
        is_underground = result[3]
        building_main_no = result[4]
        building_sub_no = result[5]

        if not admin_code or not road_code:
            return None, None

        data = {
            'confmKey': GEOSECRETKEY,
            'admCd': admin_code,
            'rnMgtSn': road_code,
            'udrtYn': is_underground,
            'buldMnnm': building_main_no,
            'buldSlno': building_sub_no,
            'resultType': 'json'
        }

        url = 'http://www.juso.go.kr/addrlink/addrCoordApi.do?' + urlencode(data)
        response = requests.get(url=url)

        result = json.loads(response.text)['results']['juso']
        if not result:
            return None, None
        return result[0]['entX'], result[0]['entY']


if __name__ == '__main__':
    init = InitSetting()
    conn = init.conn
    with conn.cursor() as cursor:
        cursor.execute(CREATE_LOCATION_TABLE)
        conn.commit()

    location = Location()
    results = location.apartment_info()

    for result in results:
        serial_no = result[0]
        longtitude_utm, latitude_utm = location.call_juso_api(result)
        longtitude, latitude = location.to_wsg84(longtitude_utm, latitude_utm)

        if not longtitude or not latitude:
            continue

        print(serial_no, longtitude, latitude)
        with conn.cursor() as cursor:
            cursor.execute(INSERT_LOCATION.format(serial_no, longtitude, latitude))
            conn.commit()
