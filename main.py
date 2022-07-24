import time
# import json

from parser.parser_vacancy import get_links, get_vacancy, get_link_resume


if __name__ == '__main__':
    print('******************************')
    print('--- TOP VACANCY 4 U v1.00 ---')
    print()
    link_resume = input('Ссылка на Ваше резюме  ')
    print()
    resume = get_link_resume(link_resume)
    print('Загружаем информацию... Подождите')
    print()
    
    data = []
    for link_vac in get_links(resume):
        data.append(get_vacancy(link_vac, resume))
        time.sleep(1)
        
    print('Обратите внимание на следующие вакансии: ') 
    print()
    for vac in sorted(data, key=lambda x: x['lrate'], reverse=True)[:5]:
        print(f"link: {vac['link']}    concurrency: {vac['lrate']*100}%")            
    # with open('data.json', 'w', encoding='utf-8') as f:
    #    json.dump(data, f, indent=4, ensure_ascii=False)