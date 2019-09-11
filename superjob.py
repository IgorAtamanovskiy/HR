# coding: utf-8
import requests
from requests.exceptions import HTTPError
import pandas as pd
import json
import numpy as np

parameters = json.loads(open('conf.json').read())
SJ_AUTH_KEY = parameters['preferences']['superjob_auth_key']
SJ_AUTH_TOKEN = parameters['preferences']['superjob_auth_token']

def GetVacansies(url,page):
    try:
        if int(page)!=0:
            url=url+'&page='+repr(page)
        headersParams = {SJ_AUTH_KEY : SJ_AUTH_TOKEN}
        response=requests.get(url,headers=headersParams)
        response.raise_for_status()

    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')  # Python 3.6
    except Exception as err:
        print(f'Other error occurred: {err}')  # Python 3.6
    else:
        RespJson=response.json()
        return RespJson

def GetPositionSalaryEstimate(JobTitleKeywords,currency):
    #Form URL for search
    JobTitleArray=JobTitleKeywords.split(',')
    strKeywords=''
    strKeywordsCounter=0
    for x in JobTitleArray:
        if x.startswith(' '):
            x = x[1:]
        strKeywords=strKeywords + '&keywords[{0}][srws]=1&keywords[{0}][skwc]=or&keywords[{0}][keys]='.format(strKeywordsCounter) + x
        strKeywordsCounter+=1

    url='https://api.superjob.ru/2.0/vacancies/?published=1&t=4&not_archive=true&period=0' + strKeywords

    ResponseJson = GetVacansies(url,0)

    print(url)

    if ResponseJson['total']!=0:

        vacancies = ResponseJson['objects']
        df = pd.DataFrame.from_dict(vacancies)
        pagecounter=2

        while (ResponseJson['more']==True):
            ResponseJson = GetVacansies(url, pagecounter)
            vacancies = ResponseJson['objects']
            df2 = pd.DataFrame.from_dict(vacancies)
            df=df.append(df2,ignore_index=True)
            pagecounter+=1

        #salaryFilter=df['payment_from']>0
        df = df[df['payment_from']>0]
        print(df.empty)

        if df.empty:
            priceestimate = [0, 0, 0, 0, '']
        else:
            currency_filter = df['currency'] == currency.lower()
            VacanciesWithExactCurrency = df[currency_filter]

            if VacanciesWithExactCurrency.empty:
                priceestimate = [0, 0, 0, 0, '']
            else:
                archivefilter=df['is_archive'] == False
                VacanciesWithExactCurrency = VacanciesWithExactCurrency[archivefilter]

                if VacanciesWithExactCurrency.empty:
                    priceestimate = [0, 0, 0, 0, '']
                else:
                    newDFStructure={'p_from':VacanciesWithExactCurrency['payment_from'],'p_to':VacanciesWithExactCurrency['payment_to'],
                                    'avg':0,
                                    'currency':VacanciesWithExactCurrency['currency'],'profession':VacanciesWithExactCurrency['profession']}
                    newDF=pd.DataFrame(newDFStructure)

                    newDF.loc[newDF.p_to>0,'avg']=(newDF.p_from+newDF.p_to)/2
                    newDF.loc[newDF.p_to == 0, 'avg'] =newDF.p_from

                    imgpath=''

                    priceestimate = [newDF.avg.min(), newDF.avg.max(), newDF.avg.median(), round(newDF.avg.mean(), 1),imgpath]
    else:
        priceestimate = [0, 0, 0, 0, '']

    return priceestimate

if __name__ == '__main__':
    pstr=GetPositionSalaryEstimate('программист,angular','RUB')
    print(pstr)