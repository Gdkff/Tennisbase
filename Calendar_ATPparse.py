import urllib.request
from bs4 import BeautifulSoup
import re
import pymysql.cursors
import requests
import datetime
import pymysql.cursors
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import selenium.common.exceptions
import time

# Задаем промежуток лет, на выходе получаем список ссылок АТР с годом сезона и типом турнира
def year_to_html_page_atp(year):
    print('Start year_to_html_page_atp')
    html_pages_atp_list = []
    trnm_cats = ['atpgs', 'ch']
    for trnm_cat in trnm_cats:
        url = 'https://www.atptour.com/en/scores/results-archive?year=' + str(year) + '&tournamentType=' + trnm_cat
        page = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        html_page = urllib.request.urlopen(page).read()
        if trnm_cat == 'atpgs':
            trnm_type = str(1)
        elif trnm_cat == 'ch':
            trnm_type = str(2)
        html_pages_atp_list.append([year, html_page, trnm_type])
    return(html_pages_atp_list)

# Задаем текст, на выходе получаем суп страницы
def html_page_to_soup(data):
    print('Start html_page_to_soup')
    data = data.decode('utf-8')
    return(BeautifulSoup(data, 'html.parser'))

# Задаем суп страницы со списком турниров сезона, год сезона, тип тура. На выходе получаем список с данными о турнирах с одной страницы
def razbor_trnm_strings_atp(soup, trnm_year, trnm_type):
    print('Start razbor_trnm_strings_atp')
    first_trnm_data_list = []
    strings = soup.find_all('tr', class_='tourney-result')
    for string in strings:
        cells = string.find_all('td')
        try:
            trnm_cat = cells[1].find('img').get('src').replace('/assets/atpwt/images/tournament/badges/categorystamps_', '').replace('.png', '').replace('.svg', '')
        except Exception:
            trnm_cat = None
        trnm_name = cells[2].find('a').get('data-ga-label')
        if '(Cancelled)' in trnm_name:
            trnm_status = 'Cancelled'
            trnm_name = trnm_name.replace(' (Cancelled)', '')
        elif '(Suspended)' in trnm_name:
            trnm_status = 'Suspended'
            trnm_name = trnm_name.replace(' (Suspended)', '')
        else:
            trnm_status = None
        trnm_linkatp = cells[2].find('a').get('href').replace('/en/tournaments/', '').replace('/overview', '') + '/' + str(trnm_year)
# # TODO: Убрать следующую строчку перед внесением в SQL
#         trnm_linkatp = 'https://www.atptour.com/en/scores/archive/' + trnm_linkatp + '/draws'
        trnm_location = re.sub("^\s+|\n|\r|\s+$|\t|", '', cells[2].find('span', class_='tourney-location').text).split(', ')
        trnm_city = trnm_location[0]
        try:
            trnm_country = trnm_location[1]
        except Exception:
            trnm_country = None
        trnm_start_raw = re.sub("^\s+|\n|\r|\s+$|\t|", '', cells[2].find('span', class_='tourney-dates').text).split('.')
        trnm_start = datetime.date(int(trnm_start_raw[0]), int(trnm_start_raw[1]), int(trnm_start_raw[2]))
        trnm_sgl = int(re.sub("^\s+|\n|\r|\s+$|\t|", '', cells[3].find_all('span', class_='item-value')[0].text))
        trnm_dbl = int(re.sub("^\s+|\n|\r|\s+$|\t|", '', cells[3].find_all('span', class_='item-value')[1].text))
        trnm_surf = re.sub("^\s+|\n|\r|\s+$|\t|", '', cells[4].find('span', class_='item-value').text)
        trnm_door = re.sub("^\s+|\n|\r|\s+$|\t|", '', cells[4].find('span', class_='item-value').previousSibling)
        try:
            trnm_prize_m = int(''.join([x for x in re.sub("^\s+|\n|\r|\s+$|\t|", '', cells[5].find('span', class_='item-value').text) if x.isdigit()]))
            trnm_prize_v = ''.join([x for x in re.sub("^\s+|\n|\r|\s+$|\t|", '', cells[5].find('span', class_='item-value').text) if not x.isdigit()]).replace(',', '')
        except Exception:
            trnm_prize_m = None
            trnm_prize_v = None
        try:
            check_status_trnm = cells[6].find('div', class_='tourney-detail-winner').text
            trnm_status = 'Finished'
        except Exception:
            pass
        trnm_finish = None
        trnm_linkitf = None
        first_trnm_data_list.append({'trnm_start': trnm_start,
                                     'trnm_finish': trnm_finish,
                                     'trnm_year': trnm_year,
                                     'trnm_type': trnm_type,
                                     'trnm_cat': trnm_cat,
                                     'trnm_name': trnm_name,
                                     'trnm_city': trnm_city,
                                     'trnm_country': trnm_country,
                                     'trnm_status': trnm_status,
                                     'trnm_sgl': trnm_sgl,
                                     'trnm_dbl': trnm_dbl,
                                     'trnm_surf': trnm_surf,
                                     'trnm_door': trnm_door,
                                     'trnm_prize_m': trnm_prize_m,
                                     'trnm_prize_v': trnm_prize_v,
                                     'trnm_linkatp': trnm_linkatp,
                                     'trnm_linkitf': trnm_linkitf})
    return(first_trnm_data_list)

def year_to_html_page_itf(year):
    print('Start razbor_trnm_strings_atp')
    trnm_type = str(3)
    url = 'https://www.itftennis.com/en/tournament-calendar/mens-world-tennis-tour-calendar/?startdate=' + str(year)
    driver.get(url)
    time.sleep(2)
    try:
        driver.find_element(By.XPATH, '//*[@id="onetrust-accept-btn-handler"]').click()
    except Exception:
        pass
    time.sleep(1)
    soup = BeautifulSoup(driver.page_source, 'lxml')
    temp_table = soup.find('table', class_='table')
    strings_num_old = 0
    strings = temp_table.find_all('tr')
    strings_num_new = len(strings)
    while strings_num_new != strings_num_old:
        try:
            location = driver.find_element(By.XPATH, '/html/body/main/div[2]/div[2]/section/div/div/button').location
            driver.execute_script("window.scrollTo(0, " + str(location['y'] - 500) + ")")
            time.sleep(1)
            driver.find_element(By.XPATH, '/html/body/main/div[2]/div[2]/section/div/div/button').click()
# TODO: Написать вместо sleep команды ожидания загрузки
            time.sleep(1)
        except selenium.common.exceptions.NoSuchElementException:
            pass
        soup = BeautifulSoup(driver.page_source, 'lxml')
        temp_table = soup.find('table', class_='table')
        strings = temp_table.find_all('tr')
        strings_num_old = strings_num_new
        strings_num_new = len(strings)
    return(year, bytes(driver.page_source, encoding='utf-8'), trnm_type)

def razbor_trnm_strings_itf(soup, trnm_year, trnm_type):
    print('Start razbor_trnm_strings_itf')
    first_trnm_data_list = []
    month_dict = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6, 'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12}
    strings = soup.find_all('tr', {'class':['whatson-table__tournament', 'whatson-table__tournament--cancelled']})
    for string in strings:
        cells = string.find_all('td')
        try:
            trnm_linkitf = cells[0].find('a').get('href').replace('/en/tournament/', '')[0:-1]
# # TODO: Убрать следующую строчку перед внесением в SQL
#             trnm_linkitf = 'https://www.itftennis.com/en/tournament/' + trnm_linkitf
        except Exception:
            trnm_linkitf = None
        try:
            trnm_name = cells[0].find('div', class_='short').text.title()
        except Exception:
            trnm_name = None
        dates_raw_list = cells[1].find('span', class_='date').text.split(' ')
        # print('/// Dates raw ITF -', dates_raw_list)
        if dates_raw_list[1] == 'Dec' and dates_raw_list[4] == 'Jan':
            year_start = int(dates_raw_list[5]) - 1
            year_finish = int(dates_raw_list[5])
        else:
            year_start = int(dates_raw_list[5])
            year_finish = int(dates_raw_list[5])
        try:
            trnm_start = datetime.date(year_start, month_dict[dates_raw_list[1]], int(dates_raw_list[0]))
        except Exception as exp:
            trnm_start = None
            print('Error in trnm_start ITF:', exp)
        try:
            trnm_finish = datetime.date(year_finish, month_dict[dates_raw_list[4]], int(dates_raw_list[3]))
        except Exception as exp:
            trnm_finish = None
            print('Error in trnm_finish ITF:', exp)
        try:
            trnm_country = cells[2].find('span', class_='hostname').text
        except Exception:
            trnm_country = None
        try:
            trnm_city = cells[3].find('span', class_='location').text
        except Exception:
            trnm_city = None
        try:
            trnm_cat = cells[4].find('span', class_='category').text
        except Exception:
            trnm_cat = None
        trnm_prize_raw = cells[5].find('span', class_='prize-money').text.replace(',', '')
        print(trnm_prize_raw)
        try:
            temp = re.findall(r'\d+', trnm_prize_raw)
            trnm_prize_m = int(''.join(temp))
        except Exception:
            trnm_prize_m = None
        try:
            trnm_prize_v = trnm_prize_raw.replace(str(trnm_prize_m), '')
        except Exception as exp:
            trnm_prize_v = None
            print('Error in trnm_prize_v:', exp)
        surface_raw = cells[6].find('span', class_='surface').text.split(' - ')
        try:
            trnm_surf = surface_raw[1]
        except Exception:
            trnm_surf = None
        try:
            trnm_door = surface_raw[0]
        except Exception:
            trnm_door = None
        try:
            trnm_status = cells[7].find('span', class_='status').text
            if trnm_status != '':
                pass
        except Exception:
            trnm_status = None
        trnm_linkatp = None
# TODO: Написать скрипт подсчета игроков в сетках ITF
        trnm_sgl = None
        trnm_dbl = None
        first_trnm_data_list.append({'trnm_start': trnm_start,
                                     'trnm_finish': trnm_finish,
                                     'trnm_year': trnm_year,
                                     'trnm_type': trnm_type,
                                     'trnm_cat': trnm_cat,
                                     'trnm_name': trnm_name,
                                     'trnm_city': trnm_city,
                                     'trnm_country': trnm_country,
                                     'trnm_status': trnm_status,
                                     'trnm_sgl': trnm_sgl,
                                     'trnm_dbl': trnm_dbl,
                                     'trnm_surf': trnm_surf,
                                     'trnm_door': trnm_door,
                                     'trnm_prize_m': trnm_prize_m,
                                     'trnm_prize_v': trnm_prize_v,
                                     'trnm_linkatp': trnm_linkatp,
                                     'trnm_linkitf': trnm_linkitf})
    return(first_trnm_data_list)

def calenar_string_from_base(trnm_type, atp_link, itf_link, trnm_city, trnm_start):
    print('Start calenar_string_from_base')
    if trnm_type in ('1', '2'):
        which_trnm = 'trnm_linkatp'
        trnm_link = atp_link
    elif trnm_type == '3':
        which_trnm = 'trnm_linkitf'
        trnm_link = itf_link
    if trnm_link != None:
        zapros_sql = "SELECT trnm_start, trnm_finish, trnm_year, trnm_type, trnm_cat, trnm_name, trnm_city, trnm_country, " \
                     "trnm_status, trnm_sgl, trnm_dbl, trnm_surf, trnm_door, trnm_prize_m, trnm_prize_v, trnm_linkatp, " \
                     "trnm_linkitf FROM calendar_men WHERE " + which_trnm + "='" + trnm_link + "'"
    else:
        zapros_sql = "SELECT trnm_start, trnm_finish, trnm_year, trnm_type, trnm_cat, trnm_name, trnm_city, trnm_country, " \
                     "trnm_status, trnm_sgl, trnm_dbl, trnm_surf, trnm_door, trnm_prize_m, trnm_prize_v, trnm_linkatp, " \
                     "trnm_linkitf FROM calendar_men WHERE trnm_city = '" + trnm_city + "' and trnm_start = '" + str(trnm_start) + "'"
    connection = pymysql.connect(host='localhost',
                                 port=3307,
                                 user='root',
                                 password='1234',
                                 db='tennisatp_base',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    print('\n', which_trnm, trnm_link)
    with connection.cursor() as cursor:
        # cursor.execute("SELECT trnm_year, trnm_name, trnm_city, trnm_country, trnm_status, trnm_start, trnm_finish, "
        #                "trnm_type, trnm_cat, trnm_prize_m, trnm_prize_v, trnm_sgl, trnm_dbl, trnm_surf, trnm_door, "
        #                "trnm_linkatp, trnm_linkitf FROM calendar_men WHERE %s = %s", (which_trnm, trnm_link))
        # cursor.execute("SELECT trnm_year, trnm_name, trnm_city, trnm_country, trnm_status, trnm_start, trnm_finish, "
        #                "trnm_type, trnm_cat, trnm_prize_m, trnm_prize_v, trnm_sgl, trnm_dbl, trnm_surf, trnm_door, "
        #                "trnm_linkatp, trnm_linkitf FROM calendar_men WHERE trnm_linkatp='delray-beach/499/2021'")
        cursor.execute(zapros_sql)

        zn = cursor.fetchone()
        connection.commit()
    # print(zn)
    return zn

def main():
    year_start = 2021
    year_finish = 2021
    options = Options()
    global driver
    driver = webdriver.Chrome(options=options)
    calendar_data_list = []
    for year in range(year_start, year_finish + 1):
        for link in year_to_html_page_atp(year):
            calendar_data_list.append(razbor_trnm_strings_atp(html_page_to_soup(link[1]), link[0], link[2]))
        link_itf = year_to_html_page_itf(year)
        calendar_data_list.append(razbor_trnm_strings_itf(html_page_to_soup(link_itf[1]), link_itf[0], link_itf[2]))
    for calendar_string in sum(calendar_data_list, []):
        print(calendar_string)
        string_from_base = calenar_string_from_base(calendar_string['trnm_type'], calendar_string['trnm_linkatp'],
                                                    calendar_string['trnm_linkitf'], calendar_string['trnm_city'],
                                                    calendar_string['trnm_start'])
        print(string_from_base)
        for key in calendar_string:
            if calendar_string[key] != string_from_base[key]:
                if calendar_string[key] != None:
                    if key == 'trnm_name' and calendar_string['trnm_type'] != '3':
                        pass
                    # elif key == 'trnm_cat' and calendar_string['trnm_year'] == 2021:
                    #     pass
                    else:
                        print('********* ', key, ':   Calendar string =', calendar_string[key], '  String from base =', string_from_base[key])




if __name__ == '__main__':
    main()
    driver.close()


# connection = pymysql.connect(host='localhost',
#                              user='root',
#                              password='1234',
#                              db='tennisatp_base',
#                              charset='utf8mb4',
#                              cursorclass=pymysql.cursors.DictCursor)
#
# trnm_year_start = 2022
# trnm_year_finish = 2023
# for trnm_year in range(trnm_year_start, trnm_year_finish):
#     trnm_cats = ['atpgs', 'ch']
#     for trnm_cat in trnm_cats:
#         url = 'https://www.atptour.com/en/scores/results-archive?year=' + str(trnm_year) + '&tournamentType=' + trnm_cat
#         print(url)
#         page = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
#         infile = urllib.request.urlopen(page).read()
#         data = infile.decode('utf-8')
#         soup = BeautifulSoup(data, 'html.parser')
#
#         strings = soup.find_all('tr', class_='tourney-result')
#         for string in strings:
#             trnm_linkatp = 'temporary link'
#             with connection.cursor() as cursor:
#                 cursor.execute("INSERT INTO calendar_try2021 (trnm_year, trnm_linkatp) VALUES (%s, %s)",
#                                (trnm_year, trnm_linkatp))
#                 cursor.execute("SELECT trnm_id FROM calendar_try2021 WHERE trnm_linkatp=%s", (trnm_linkatp))
#                 pr = cursor.fetchone()
#             connection.commit()
#             print('****************')
#             trnm_id = pr['trnm_id']
#             print('ID турнира:', trnm_id)
#             print('Год проведения турнира:', trnm_year)
#             rows = string.find_all('td')
#             if trnm_cat == 'atpgs':
#                 trnm_type = '1'
#             if trnm_cat == 'ch':
#                 trnm_type = '2'
#             if trnm_cat == 'fu':
#                 trnm_type = '3'
#             print('Тип турнира', trnm_type)
#             with connection.cursor() as cursor:
#                 cursor.execute("UPDATE calendar_try2021 SET trnm_type = %s WHERE trnm_id = %s",
#                                (trnm_type, trnm_id))
#             connection.commit()
#             num = 0
#             # days_list_clear = list()
#             for row in rows:
#                 num = num + 1
#                 if num == 2:
#                     img_link = row.find('img')
#                     try:
#                         trnm_cat = img_link.get('src').replace('/assets/atpwt/images/tournament/badges/categorystamps_',
#                                                                '').replace('.png', '').replace('.svg', '')
#                         print('Категория турнира:', trnm_cat)
#                         with connection.cursor() as cursor:
#                             cursor.execute("UPDATE calendar_try2021 SET trnm_cat = %s WHERE trnm_id = %s",
#                                            (trnm_cat, trnm_id))
#                         connection.commit()
#                     except Exception:
#                         print('!!! Cat_trnm-fail')
#                 if num == 3:
#                     trnm_name_and_sts = re.sub("^\s+|\n|\r|\s+$|\t|", '', row.find('a', class_='tourney-title').text)
#                     if '(Cancelled)' in trnm_name_and_sts or '(Postponed)' in trnm_name_and_sts or '(Suspended)' in trnm_name_and_sts:
#                         trnm_name_and_sts_lst = trnm_name_and_sts.split(' (')
#                         trnm_status = trnm_name_and_sts_lst[1].replace(')', '')
#                         print(trnm_status)
#                         with connection.cursor() as cursor:
#                             cursor.execute("UPDATE calendar_try2021 SET trnm_status = %s WHERE trnm_id = %s",
#                                            (trnm_status, trnm_id))
#                         connection.commit()
#                         trnm_name = trnm_name_and_sts_lst[0]
#                     else:
#                         trnm_name = trnm_name_and_sts
#                     print('Название турнира:', trnm_name)
#                     with connection.cursor() as cursor:
#                         cursor.execute("UPDATE calendar_try2021 SET trnm_name = %s WHERE trnm_id = %s",
#                                        (trnm_name, trnm_id))
#                     connection.commit()
#                     trnm_location = row.find('span', class_='tourney-location').text.split(', ')
#                     try:
#                         trnm_city = re.sub("^\s+|\n|\r|\s+$|\t|", '', trnm_location[0])
#                         print('Город:', trnm_city)
#                         with connection.cursor() as cursor:
#                             cursor.execute("UPDATE calendar_try2021 SET trnm_city = %s WHERE trnm_id = %s",
#                                            (trnm_city, trnm_id))
#                         connection.commit()
#                     except IndexError:
#                         print('!!! City-fail')
#                     try:
#                         trnm_country = re.sub("^\s+|\n|\r|\s+$|\t|", '', trnm_location[1])
#                         print('Страна:', trnm_country)
#                         with connection.cursor() as cursor:
#                             cursor.execute("UPDATE calendar_try2021 SET trnm_country = %s WHERE trnm_id = %s",
#                                            (trnm_country, trnm_id))
#                         connection.commit()
#                     except IndexError:
#                         print('!!! Country-fail')
#                     trnm_start = row.find('span', class_='tourney-dates').text
#                     trnm_start = re.sub("^\s+|\n|\r|\s+$|\t|", '', trnm_start)
#                     print('Дата начала турнира:', trnm_start)
#                     with connection.cursor() as cursor:
#                         cursor.execute("UPDATE calendar_try2021 SET trnm_start = %s WHERE trnm_id = %s",
#                                        (trnm_start, trnm_id))
#                     connection.commit()
#                 if num == 4:
#                     trnm_sgl_dbl = row.find_all('span', class_='item-value')
#                     try:
#                         trnm_sgl = trnm_sgl_dbl[0].text
#                         trnm_sgl = re.sub("^\s+|\n|\r|\s+$|\t|", '', trnm_sgl)
#                         print('Количество игроков SGL:', trnm_sgl)
#                         with connection.cursor() as cursor:
#                             cursor.execute("UPDATE calendar_try2021 SET trnm_sgl = %s WHERE trnm_id = %s",
#                                            (trnm_sgl, trnm_id))
#                         connection.commit()
#                     except IndexError:
#                         print('!!! SGL-fail')
#                     try:
#                         trnm_dbl = trnm_sgl_dbl[1].text
#                         trnm_dbl = re.sub("^\s+|\n|\r|\s+$|\t|", '', trnm_dbl)
#                         print('Количество игроков DBL:', trnm_dbl)
#                         with connection.cursor() as cursor:
#                             cursor.execute("UPDATE calendar_try2021 SET trnm_dbl = %s WHERE trnm_id = %s",
#                                            (trnm_dbl, trnm_id))
#                         connection.commit()
#                     except IndexError:
#                         print('!!! DBL-fail')
#                 if num == 5:
#                     trnm_surf = row.find('span', class_='item-value').text
#                     trnm_surf = re.sub("^\s+|\n|\r|\s+$|\t|", '', trnm_surf)
#                     print('Покрытие:', trnm_surf)
#                     with connection.cursor() as cursor:
#                         cursor.execute("UPDATE calendar_try2021 SET trnm_surf = %s WHERE trnm_id = %s",
#                                        (trnm_surf, trnm_id))
#                     connection.commit()
#                     trnm_door = row.find('span', class_='item-value').previousSibling
#                     trnm_door = re.sub("^\s+|\n|\r|\s+$|\t|", '', trnm_door)
#                     print('Indoor/Outdoor:', trnm_door)
#                     with connection.cursor() as cursor:
#                         cursor.execute("UPDATE calendar_try2021 SET trnm_door = %s WHERE trnm_id = %s",
#                                        (trnm_door, trnm_id))
#                     connection.commit()
#                 if num == 6:
#                     try:
#                         trnm_prize_mv = row.find('span', class_='item-value').text
#                         trnm_prize_mv = re.sub("^\s+|\n|\r|\s+$|\t|", '', trnm_prize_mv).replace(',', "")
#                         trnm_prize_m = ''.join(re.findall(r'\d+', trnm_prize_mv))
#                         print('Призовой фонд:', trnm_prize_m)
#                         with connection.cursor() as cursor:
#                             cursor.execute("UPDATE calendar_try2021 SET trnm_prize_m = %s WHERE trnm_id = %s",
#                                            (trnm_prize_m, trnm_id))
#                         connection.commit()
#                         trnm_prize_v = trnm_prize_mv.replace(trnm_prize_m, '')
#                         print('Валюта:', trnm_prize_v)
#                         with connection.cursor() as cursor:
#                             cursor.execute("UPDATE calendar_try2021 SET trnm_prize_v = %s WHERE trnm_id = %s",
#                                            (trnm_prize_v, trnm_id))
#                         connection.commit()
#                     except AttributeError:
#                         print('!!! Prize-fail')
#                 if num == 8:
#                     try:
#                         trnm_linkatp = row.find('a').get('href').replace('/en/scores/archive/', '').replace('/results',
#                                                                                                             '')
#                         print('Ссылка:', trnm_linkatp)
#                         with connection.cursor() as cursor:
#                             cursor.execute("UPDATE calendar_try2021 SET trnm_linkatp = %s WHERE trnm_id = %s",
#                                            (trnm_linkatp, trnm_id))
#                         connection.commit()
#                         url2 = 'https://www.atptour.com/en/scores/archive/' + trnm_linkatp + '/results'
#                         # print(url2)
#                         page2 = urllib.request.Request(url2, headers={'User-Agent': 'Mozilla/5.0'})
#                         infile2 = urllib.request.urlopen(page2).read()
#                         data2 = infile2.decode('utf-8')
#                         soup2 = BeautifulSoup(data2, 'html.parser')
#                         trnm_duration = soup2.find('span', class_='tourney-dates').text
#                         trnm_duration = re.sub("^\s+|\n|\r|\s+$|\t|", '', trnm_duration).split(' - ')
#                         print('Дата окончания турнира:', trnm_duration[1])
#                         with connection.cursor() as cursor:
#                             cursor.execute("UPDATE calendar_try2021 SET trnm_finish = %s WHERE trnm_id = %s",
#                                            (trnm_duration[1], trnm_id))
#                         connection.commit()
#                         try:
#                             if trnm_year == 2021:
#                                 trnm_qual_start = ''
#                                 days_soup = soup2.find('div', class_='dropdown-holder')
#                                 days_list = days_soup.find_all('li')
#                                 low_day = '2222-12-31'
#                                 for day in days_list:
#                                     if day.text != 'Date':
#                                         if low_day > day.text:
#                                             low_day = day.text
#                                         # days_list_clear.append(day.text)
#                                 if low_day < trnm_start:
#                                     trnm_qual_start = low_day
#                                 print('Дата начала квалификации:', trnm_qual_start)
#                                 with connection.cursor() as cursor:
#                                     cursor.execute("UPDATE calendar_try2021 SET trnm_qual_start = %s WHERE trnm_id = %s",
#                                                    (trnm_qual_start, trnm_id))
#                                 connection.commit()
#                         except Exception:
#                             print('!!! Qual-fail')
#                     except AttributeError:
#                         print('!!! Link-fail')
#
#             if trnm_cat == '250':
#                 trnm_poi = 250
#             elif trnm_cat == '2000':
#                 trnm_poi = 2000
#             elif trnm_cat == '500':
#                 trnm_poi = 500
#             elif trnm_cat == 'atpcup':
#                 trnm_poi = 750
#             # elif trnm_cat == 'challenger':
#             #     if trnm_prize_m>
#             #     trnm_poi = 750
#             else:
#                 trnm_poi = 0
#             if trnm_poi == 0:
#                 print('!!! Prize_points - fail')
#             else:
#                 print('Призовые очки максимально:', trnm_poi)
#             rec_dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#             print(rec_dt)
#             with connection.cursor() as cursor:
#                 cursor.execute("UPDATE calendar_try2021 SET rec_dt = %s WHERE trnm_id = %s",
#                                (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), trnm_id))
#                 if trnm_linkatp == 'temporary link':
#                     cursor.execute("UPDATE calendar_try2021 SET trnm_linkatp = NULL WHERE trnm_id = %s", (trnm_id))
#             connection.commit()
#
#     month_dict = {'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04', 'May': '05', 'Jun': '06', 'Jul': '07',
#                   'Aug': '08', 'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'}
#     schetchik = 0
#     options = Options()
#     # options.add_argument('--headless')
#     # options.add_argument('--disable-gpu')
#     driver = webdriver.Chrome(options=options)
#     url = 'https://www.itftennis.com/en/tournament-calendar/mens-world-tennis-tour-calendar/?startdate=' + str(trnm_year)
#     print(url)
#     driver.get(url)
#     driver.maximize_window()
#     time.sleep(2)
#     soup1 = BeautifulSoup(driver.page_source, 'lxml')
#     temp_table = soup1.find('table', class_='table')
#     strings_num_old = 0
#     strings = temp_table.find_all('tr')
#     strings_num_new = len(strings)
#     print('Количество строк:', strings_num_new-1)
#     driver.find_element_by_xpath('//*[@id="onetrust-accept-btn-handler"]').click()
#     while strings_num_new != strings_num_old:
#         try:
#             location = driver.find_element_by_xpath('/html/body/main/div[2]/div[2]/section/div/div/button').location
#             driver.execute_script("window.scrollTo(0, " + str(location['y'] - 500) + ")")
#             time.sleep(2)
#             driver.find_element_by_xpath('/html/body/main/div[2]/div[2]/section/div/div/button').click()
#             time.sleep(3)
#         except selenium.common.exceptions.NoSuchElementException:
#             pass
#         soup1 = BeautifulSoup(driver.page_source, 'lxml')
#         temp_table = soup1.find('table', class_='table')
#         strings = temp_table.find_all('tr')
#         strings_num_old = strings_num_new
#         strings_num_new = len(strings)
#         print('Количество строк:', strings_num_new-1)
#
#     for string in strings[1:]:
#         schetchik += 1
#         print('******************************')
#         print(schetchik)
#         rows = string.find_all('td')
#         num = 0
#         link_itf = None
#         for row in rows:
#             num += 1
#             if num == 1:
#                 try:
#                     link_itf = row.find('a').get('href').replace('/en/tournament/', '')[0:-1]
#                     print(link_itf)
#                 except Exception:
#                     print('!!! Link-fail')
#                 try:
#                     trnm_name = row.find('div', class_='short').text.title()
#                     print(trnm_name)
#                 except Exception:
#                     print('!!! Name-fail')
#             if num == 2:
#                 dates_raw_list = row.find('span', class_='date').text.split(' ')
#                 try:
#                     trnm_start = dates_raw_list[5] + '-' + month_dict[dates_raw_list[1]] + '-' + dates_raw_list[0]
#                     print(trnm_start)
#                 except Exception:
#                     print('!!! Start-fail')
#                 try:
#                     trnm_finish = dates_raw_list[5] + '-' + month_dict[dates_raw_list[4]] + '-' + dates_raw_list[3]
#                     print(trnm_finish, type(trnm_finish))
#                 except Exception:
#                     print('!!! Finish-fail')
#             if num == 3:
#                 try:
#                     trnm_country = row.find('span', class_='hostname').text
#                     check_country = trnm_country
#                     wright_country = '%' + check_country + '%'
#                     with connection.cursor() as cursor:
#                         cursor.execute(
#                             "SELECT id, name_1, name_2, name_3 FROM tennisatp_base.countries where name_1 like %s or name_2 like %s or name_3 like %s",
#                             (wright_country, wright_country, wright_country))
#                         id_country = cursor.fetchall()
#                     connection.commit()
#                     if len(id_country) > 1:
#                         with connection.cursor() as cursor:
#                             cursor.execute(
#                                 "SELECT id, name_1, name_2, name_3 FROM tennisatp_base.countries where name_1 like %s or name_2 like %s or name_3 like %s",
#                                 (check_country, check_country, check_country))
#                             id_country = cursor.fetchall()
#                         connection.commit()
#                     if len(id_country) == 1:
#                         id_country = id_country[0]['id']
#                         print(id_country, type(id_country))
#                     else:
#                         id_country = None
#                 except Exception:
#                     print('!!! Country-fail')
#             if num == 4:
#                 try:
#                     trnm_city = row.find('span', class_='location').text
#                     print(trnm_city, type(trnm_city))
#                 except Exception:
#                     print('!!! City-fail')
#             if num == 5:
#                 try:
#                     trnm_cat = row.find('span', class_='category').text
#                     print(trnm_cat, type(trnm_cat))
#                 except Exception:
#                     print('!!! Category-fail')
#             if num == 6:
#                 trnm_prize_raw = row.find('span', class_='prize-money').text.replace(',', '')
#                 try:
#                     temp = re.findall(r'\d+', trnm_prize_raw)
#                     trnm_prize_m = ''.join(temp)
#                     print(trnm_prize_m, type(trnm_prize_m))
#                 except Exception:
#                     print('!!! Money-fail')
#                 try:
#                     trnm_prize_v = trnm_prize_raw.replace(trnm_prize_m, '')
#                     print(trnm_prize_v, type(trnm_prize_v))
#                 except Exception:
#                     print('!!! $-fail')
#             if num == 7:
#                 surface_raw = row.find('span', class_='surface').text.split(' - ')
#                 try:
#                     trnm_surf = surface_raw[1]
#                     print(trnm_surf, type(trnm_surf))
#                 except Exception:
#                     print('!!! Surface-fail')
#                 try:
#                     trnm_door = surface_raw[0]
#                     print(trnm_door, type(trnm_door))
#                 except Exception:
#                     print('!!! Door-fail')
#             if num == 8:
#                 try:
#                     trnm_status = row.find('span', class_='status').text
#                     if trnm_status != '':
#                         print(trnm_status, type(trnm_status))
#                 except Exception:
#                     print('!!! Status-fail')
#                     trnm_status = None
#         with connection.cursor() as cursor:
#             cursor.execute("INSERT INTO calendar_try2021 (trnm_year, trnm_name, trnm_city, trnm_country, trnm_status, "
#                            "trnm_start, trnm_finish, trnm_type, trnm_prize_m, trnm_prize_v, trnm_surf, trnm_door,"
#                            "trnm_linkitf) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
#                            (trnm_year, trnm_name, trnm_city, id_country, trnm_status, trnm_start, trnm_finish,
#                             '3', trnm_prize_m, trnm_prize_v, trnm_surf, trnm_door, link_itf))
#             connection.commit()