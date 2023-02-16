from contextlib import contextmanager

import requests
import fake_useragent
from  celery.result import _set_task_join_will_block, task_join_will_block
from celery.utils.log import get_task_logger
from bs4 import BeautifulSoup

from .main import app


logger = get_task_logger(__name__)


@contextmanager
def allow_join_result():
    'To bypass blocking celery'
    reset_value = task_join_will_block()
    _set_task_join_will_block(False)
    try:
        yield
    finally:
        _set_task_join_will_block(reset_value)


@app.task(bind=True)
def main_parse(self, link: str) -> dict:
    '''
    Main function for parsing. We receive the client's resume, analyze it, look for suitable vacancies and analyze them.
    Args:
        self: To update the status of a task
        link(str): Link to the user's resume

    Returns:
        all_vac(dict): All relevant sorted vacancies
    '''

    resume = parse_resume.delay(link)
    with allow_join_result():
        resume = resume.get()
    self.update_state(state='TOOK_RESUME',
                      meta={'client_resume': resume['vacancy']})
    experience = {
        'irrelevant': '',
        'low': '&experience=between1And3',
        'mid': '&experience=between3And6',
        'hard': '&experience=moreThan6',
        'noexp': '&experience=noExperience'
    }

    if len(resume['exp']) == 0 or resume['exp'].split(' ')[1][0] == 'м':
        exp = experience['noexp']
    else:
        if int(resume['exp'].split(' ')[0]) < 3:
            exp = experience['low']
        elif int(resume['exp'].split(' ')[0]) < 6:
            exp = experience['mid']
        else:
            exp = experience['hard']

    text = resume['vacancy'].strip().replace(' ', '+').lower()
    ua = fake_useragent.UserAgent()
    res = requests.get(
        url=f'https://hh.ru/search/vacancy?area=2{exp}\
        &search_field=name&search_field=company_name&\
        search_field=description&text={text}\
        &from=suggest_post&page=0',
        headers={"user-agent": ua.random}
    )
    if res.status_code != 200:
        return {'Link': 'error'}
    soup = BeautifulSoup(res.content, "lxml")
    try:
        page_count = int(soup.find("div", attrs={"class": "pager"}).find_all(
            "span", recursive=False)[-1].find("a").find("span").text)
    except:
        page_count = 1
    all_vac = []
    for page in range(page_count):
        try:
            res = requests.get(
                url=f'https://hh.ru/search/vacancy?area=2{exp}\
                &search_field=name&search_field=company_name\
                &search_field=description&text={text}&from=suggest_post&page={page}',
                headers={"user-agent": ua.random}
            )
            if res.status_code == 200:
                soup = BeautifulSoup(res.content, "lxml")
                find_vac = soup.find_all("a", attrs={'class': "serp-item__title",
                                                     "data-qa": "serp-item__title"})
                vacancies = len(find_vac)
                link_number = 0
                for link in find_vac:
                    link_number += 1
                    parse_vac = get_vacancy.delay(link.attrs["href"].split("?")[0], resume)
                    with allow_join_result():
                        parse_vac = parse_vac.get()
                    all_vac.append(parse_vac)
                    self.update_state(state='PROGRESS',
                                      meta={'current': link_number,
                                            'total': vacancies,
                                            'status': parse_vac['name']}
                                      )
                    logger.info('Now:', parse_vac)
            else:
                print('!=200')
                logger.info('ERROR 200')
        except Exception as e:
            print(f"Ошибочка вышла {e}")
        #sort by rating
        all_vac = sorted(all_vac, key=lambda x: x['lrate'], reverse=True)
        return {'current': 100, 'total': 100, 'status': 'Find completed!', 'result': all_vac}


@app.task()
def parse_resume(link: str) -> dict:
    '''
    Function for parsing key arguments from a client's resume
    Args:
        link(str): Link to the user's resume

    Returns:
        res_resume(dict): Dictionary with job title, experience and skills
    '''
    logger.info('parse_resume - Starting work ')
    ua = fake_useragent.UserAgent()
    res = requests.get(
        url=link,
        headers={"user-agent": ua.random}
    )
    if res.status_code != 200:
        logger.info('Error: status_code != 200 ')
        return {}

    try:
        if res.status_code == 200:
            soup = BeautifulSoup(res.content, "lxml")

            name_vac = soup.find('span', attrs={"class": "resume-block__title-text"})
            exps = ' '.join([expa.text.replace("\xa0", " ") for expa in soup.find(
                'span',
                attrs={"class": "resume-block__title-text resume-block__title-text_sub"})
                            .find_all('span')])
            tags = [tag.text for tag in soup.find(attrs={"class": "bloko-tag-list"})\
                .find_all("div", attrs={"class": "bloko-tag bloko-tag_inline bloko-tag_countable"})]

            res_resume = {'vacancy': name_vac.text, 'exp': exps, 'tags': tags}
            logger.info('Work Finished ')
            return res_resume
    except Exception as e:
        print(f"ERROOOOOR {e}")


@app.task()
def get_vacancy(link: str, resume: dict) -> dict:
    '''
    Function for parsing a single vacancy
    Args:
        link(str): Job posting link
        resume: Dictionary with job title, experience and skills

    Returns:
        dict: Job data after parsing
    '''

    logger.info('Get Vacancy - Starting work ')
    ua = fake_useragent.UserAgent()
    data = requests.get(url=link, headers={"user-agent": ua.random})
    if data.status_code != 200:
        return {}
    soup = BeautifulSoup(data.content, "lxml")
    try:
        name = soup.find('h1', attrs={"data-qa": "vacancy-title"}).text
    except:
        name = ""
    try:
        salary = soup.find(attrs={"data-qa": "vacancy-salary"}).text.replace("\u2009", "")\
            .replace("\xa0", " ")
    except:
        salary = ""
    count = 0
    try:

        tags = []
        for tag in soup.find(attrs={"class": "bloko-tag-list"})\
                .find_all("span", attrs={"class": "bloko-tag__section_text"}):
            if tag.text in resume['tags']:
                count += 1
            tags.append(tag.text)
    except:
        tags = []
    try:
        lrate = round(count/len(tags)*100)
    except ZeroDivisionError:
        lrate = 0

    return {
        "name": name,
        "salary": salary,
        "tags": tuple(tags),
        "link": link,
        "lrate": lrate,
    }
