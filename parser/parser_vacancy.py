import time

import requests
import fake_useragent
from bs4 import BeautifulSoup


def get_link_resume(link):
    ua = fake_useragent.UserAgent()    
    res = requests.get(
        url=link,
        headers={"user-agent": ua.random}
    )
    if res.status_code != 200:
        return print('ERROR :c')

    try:
        if res.status_code == 200:
            soup = BeautifulSoup(res.content, "lxml")
            name_vac = soup.find('span', attrs={"class": "resume-block__title-text"})
            exps = ' '.join([expa.text.replace("\xa0", " ") for expa in soup.find(
                'span', attrs={"class": "resume-block__title-text resume-block__title-text_sub"})\
                    .find_all('span')])
            tags = [tag.text for tag in soup.find(attrs={"class": "bloko-tag-list"}).find_all(
                "div", attrs={"class": "bloko-tag bloko-tag_inline bloko-tag_countable"})]
            res_resume = {'vacancy': name_vac.text, 'exp': exps, 'tags': tags}

    except Exception as e:
        print(f"ERROOOOOR {e}")
    return res_resume


def get_links(resume):
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
        url=f'https://hh.ru/search/vacancy?area=2{exp}&search_field=name&search_field=company_name&search\
            _field=description&text={text}&from=suggest_post&page=0',
        headers={"user-agent": ua.random}
    )
    if res.status_code != 200:
        return print('Link error')
    soup = BeautifulSoup(res.content, "lxml")
    try:
        page_count = int(soup.find("div", attrs={"_class": "pager"}).find_all(
            "span", recursive=False)[-1].find("a").find("span").text)
    except:
        page_count = 1
        
    for page in range(page_count):
        try:
            res = requests.get(
                url=f'https://hh.ru/search/vacancy?area=2{exp}&search_field=name&search_field=company_name\
                    &search_field=description&text={text}&from=suggest_post&page={page}',
                headers={"user-agent": ua.random}
            )
            if res.status_code == 200:
                soup = BeautifulSoup(res.content, "lxml")
                for a in soup.find_all(
                        "a", attrs={'class': "bloko-link", "data-qa": "vacancy-serp__vacancy-title"}):
                    yield f'{a.attrs["href"].split("?")[0]}'
            else: 
                print('!=200')
        except Exception as e:
            print(f"Ошибочка вышла {e}")
        time.sleep(1)


def get_vacancy(link, resume):
    ua = fake_useragent.UserAgent()
    data = requests.get(
        url=link,
        headers={"user-agent": ua.random}
    )
    if data.status_code != 200:
        return
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
    try:
        count = 0
        tags = []    
        for tag in soup.find(attrs={"class": "bloko-tag-list"})\
                .find_all("span", attrs={"class": "bloko-tag__section_text"}):
            if tag.text in resume['tags']:
                count += 1                                    
            tags.append(tag.text)  
    except:
        tags = []
    try: 
        lrate = count/len(tags)
    except ZeroDivisionError:
        lrate = 0
    resume = {
        "name": name,
        "salary": salary,
        "tags": tuple(tags),
        "link": link,
        "lrate": lrate,
    }
    return resume
