# coding: utf-8
import requests
import pandas as pd
import datetime

def GetPositionSalaryEstimate(JobTitle,currency):
    number_of_pages = 10
    job_title = [JobTitle]# ["'Frontend developer' and 'Angular' and 'Senior'"]
    for job in job_title:
        data=[]
        for i in range(number_of_pages):
            url = 'https://api.hh.ru/vacancies'
            par = {'text': job, 'area':'1','per_page':'10', 'page':i}
            r = requests.get(url, params=par)
            e=r.json()
            data.append(e)
            vacancy_details = data[0]['items'][0].keys()
            df = pd.DataFrame(columns=list(vacancy_details))
            ind = 0
            for i in range(len(data)):
                for j in range(len(data[i]['items'])):
                    df.loc[ind] = data[i]['items'][j]
                    ind+=1

        salaries = df.salary.dropna()
        VacDescription=df.snippet
        #print(VacDescription)

        frm=[x['from'] for x in salaries]
        to = [x['to'] for x in salaries]
        cur=[x['currency'] for x in salaries]

        descr=[x['requirement'] for x in VacDescription]
        VD={'Description':descr}
        VD_DF=pd.DataFrame(VD)
        print(VD_DF)

        d={'from':frm,'to':to,'currency':cur}
        ddf=pd.DataFrame(d)

        currency_filter=ddf['currency']==currency
        ddfc=ddf[currency_filter]

        #wordcloud

        from collections import Counter
        vacancy_names = df.name
        cloud = Counter(vacancy_names)
        #print(cloud)
        from wordcloud import WordCloud, STOPWORDS
        stopwords = set(STOPWORDS)
        cloud = ''
        for x in list(vacancy_names):
            cloud += x + ' '
        wordcloud = WordCloud(width=800, height=800,

                              stopwords=stopwords,
                              min_font_size=8, background_color='white'
                              ).generate(cloud)

        import matplotlib.pylab as plt
        plt.figure(figsize=(16, 16))
        plt.axis("off")
        plt.imshow(wordcloud)
        imgpath="imgs\\" + repr(datetime.datetime.now().timestamp())+'_vacancy_cloud.png'
        plt.savefig(imgpath)

        priceestimate = [ddfc['from'].min(), ddfc['to'].max(), ddfc['to'].median(), round(ddfc['to'].mean(), 1),imgpath]

    return priceestimate

        #print(repr(ddfc['from'].min()) + ' ' + repr(ddfc['to'].max()) + ' ' + repr(ddfc['to'].median()) + ' ' + repr(ddfc['to'].mean()))

if __name__ == '__main__':
    price=GetPositionSalaryEstimate("'Frontend developer' and 'React'",'RUR')