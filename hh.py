# coding: utf-8
import requests
import pandas as pd
import datetime
import json


def GetDataFromSupplier(JobTitle):
    number_of_pages = 10
    job = JobTitle
    data = []
    for i in range(number_of_pages):
        url = "https://api.hh.ru/vacancies"
        par = {"text": job, "area": "1", "per_page": "10", "page": i}
        r = requests.get(url, params=par)
        e = r.json()
        data.append(e)

    filename = job
    filename = filename.replace(" AND ", "-").replace("'", "")
    filename = "responses\hh-" + filename + ".json"
    outfile = open(filename, "w+")
    json.dump(data, outfile)
    outfile.close()

    return data


def GetPositionSalaryEstimate(JobTitle, currency):

    JsonData = GetDataFromSupplier(JobTitle)

    vacancy_details = JsonData[0]["items"][0].keys()
    df = pd.DataFrame(columns=list(vacancy_details))
    ind = 0
    for i in range(len(JsonData)):
        for j in range(len(JsonData[i]["items"])):
            df.loc[ind] = JsonData[i]["items"][j]
            ind += 1

    print(df)

    salaries = df.salary
    df_names = df.name

    print(df_names)


    VacDescription = df.snippet

    dfJoin = pd.concat([df_names, salaries], axis=1)

    dfJoinWONA = dfJoin.salary.dropna()

    print(dfJoinWONA)

    # print(salaries.head())

    frm = [x["from"] for x in salaries]
    to = [x["to"] for x in salaries]
    cur = [x["currency"] for x in salaries]

    descr = [x["requirement"] for x in VacDescription]

    VD = {"Description": descr}
    VD_DF = pd.DataFrame(VD)

    d = {"from": frm, "to": to, "currency": cur}
    ddf = pd.DataFrame(d)

    dfVacNameWPrice = pd.concat([df.name, ddf], axis=1)

    print(dfVacNameWPrice)

    currency_filter = ddf["currency"] == currency
    ddfc = ddf[currency_filter]

    # wordcloud

    from collections import Counter

    vacancy_names = df.name
    cloud = Counter(vacancy_names)
    # print(cloud)
    from wordcloud import WordCloud, STOPWORDS

    stopwords = set(STOPWORDS)
    cloud = ""
    for x in list(vacancy_names):
        cloud += x + " "

    wordcloud = WordCloud(
        width=800,
        height=800,
        stopwords=stopwords,
        min_font_size=8,
        background_color="black",
    ).generate(cloud)

    import matplotlib.pylab as plt

    plt.figure(figsize=(16, 16))
    plt.axis("off")
    plt.imshow(wordcloud)
    imgpath = (
        "imgs\\" + repr(datetime.datetime.now().timestamp()) + "_vacancy_cloud.png"
    )
    plt.savefig(imgpath)

    print(ddfc)

    priceestimate = [
        ddfc["from"].min(),
        ddfc["to"].max(),
        ddfc["to"].median(),
        round(ddfc["to"].mean(), 1),
        imgpath,
        ddfc,
    ]

    return priceestimate


if __name__ == "__main__":
    GetPositionSalaryEstimate("'angular' AND 'Frontend Developer'" , "RUB")

    #print(range(len(JsonData)))

    # price=GetPositionSalaryEstimate("'секретарь'",'RUR')
