GRANT_DB_TO_USER = "GRANT ALL PRIVILEGES ON DATABASE %s TO %s;"
CREATE_SCHEMA = "create schema apartment;"

CREATE_CITY_TABLE = """create table apartment.city(
	city_code varchar(50) not null unique,
	city_name varchar(50) null)
"""

INSERT_CITY_DATA="""
insert into apartment.city (city_code, city_name) values(11110,'종로구');
insert into apartment.city (city_code, city_name) values(11140,'중구');
insert into apartment.city (city_code, city_name) values(11170,'용산구');
insert into apartment.city (city_code, city_name) values(11200,'성동구');
insert into apartment.city (city_code, city_name) values(11215,'광진구');
insert into apartment.city (city_code, city_name) values(11230,'동대문구');
insert into apartment.city (city_code, city_name) values(11260,'중랑구');
insert into apartment.city (city_code, city_name) values(11290,'성북구');
insert into apartment.city (city_code, city_name) values(11305,'강북구');
insert into apartment.city (city_code, city_name) values(11320,'도봉구');
insert into apartment.city (city_code, city_name) values(11350,'노원구');
insert into apartment.city (city_code, city_name) values(11380,'은평구');
insert into apartment.city (city_code, city_name) values(11410,'서대문구');
insert into apartment.city (city_code, city_name) values(11440,'마포구');
insert into apartment.city (city_code, city_name) values(11470,'양천구');
insert into apartment.city (city_code, city_name) values(11500,'강서구');
insert into apartment.city (city_code, city_name) values(11530,'구로구');
insert into apartment.city (city_code, city_name) values(11545,'금천구');
insert into apartment.city (city_code, city_name) values(11560,'영등포구');
insert into apartment.city (city_code, city_name) values(11590,'동작구');
insert into apartment.city (city_code, city_name) values(11620,'관악구');
insert into apartment.city (city_code, city_name) values(11650,'서초구');
insert into apartment.city (city_code, city_name) values(11680,'강남구');
insert into apartment.city (city_code, city_name) values(11710,'송파구');
insert into apartment.city (city_code, city_name) values(11740,'강동구');
"""

CREATE_TRANSACTION_TABLE="""create table apartment.transaction(
	price_no serial primary key,
	price int default 0,
	built_year int default 0,
	road_name varchar(100),
	road_building_main_code varchar(10),
	road_building_sub_code varchar(10),
	road_city_code varchar(10),
	road_serial_code varchar(10),
	road_basement_code varchar(10),
	road_code varchar(10),
	region_name varchar(20),
	region_main_code varchar(10),
	region_sub_code varchar(10),
	region_city_code varchar(10),
	region_city2_code varchar(10),
	region_zip_code varchar(10),
	apart_name varchar(100),
        year varchar(5),
	month varchar(5),
	day varchar(10),
	serial_no varchar(20),
	size float(2),
	zip_code varchar(10),
	city_code varchar(10) references apartment.city(city_code) null,
	floor int)
"""

GENERATE_SERIAL_NO="""
update apartment."transaction"
set serial_no = region_city_code||'-'||region_city2_code||'-'||road_code
where serial_no is null;
"""

SELECT_TRANSACTION_FOR_LOCATION= """
SELECT * FROM (
	SELECT
		serial_no,
		region_city_code || region_city2_code,
		region_city_code || road_code,
		0,
		road_building_main_code,
		road_building_sub_code
	FROM
		apartment. "transaction"
	GROUP BY
		serial_no,
		region_city_code,
		region_city2_code,
		road_code,
		road_building_main_code,
		road_building_sub_code) AS e
WHERE
	NOT EXISTS (
		SELECT 1
		FROM apartment.location AS l
		WHERE l.serial_no = e.serial_no);
"""


CREATE_LOCATION_TABLE="""
    CREATE TABLE apartment.location (
            location_no serial PRIMARY KEY,
            serial_no varchar(50),
            longitude_x FLOAT,
            latitude_y float
    );
"""

INSERT_LOCATION = """
    insert into apartment.location (serial_no, longitude_x, latitude_y) values('{}', '{}', '{}');
    """
