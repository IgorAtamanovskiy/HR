# coding: utf-8
import requests
import pandas as pd
import datetime
import json

# import os


def GetDataFromSupplier(JobTitle):
    number_of_pages = 10
    job = JobTitle

    filename = job
    filename = filename.replace(" AND ", "-").replace("'", "")
    filename = (
        "responses/hh-" + filename + repr(datetime.datetime.now().timestamp()) + ".json"
    )

    # fullpath = os.path.isfile(os.path.dirname(os.path.abspath(__file__)) + '/' + filename)

    data = []

    for i in range(number_of_pages):
        url = "https://api.hh.ru/vacancies"
        par = {"text": job, "area": "1", "per_page": "10", "page": i}
        r = requests.get(url, params=par)
        e = r.json()
        data.append(e)

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

    salaries = df.salary
    df_names = df.name

    # get vacancies descriptions for wordcloud
    VacDescription = df.snippet

    # create dataframe with names and salaries
    dfJoin = pd.concat([df_names, salaries], axis=1)

    # print(dfJoin)

    dfJoin.salary.dropna()
    print("3. Step")

    # dfJoinWONA = dfJoin.salary.dropna()

    # print(salaries.head())

    frm = [x["from"] for x in dfJoin.salary if x != None]
    to = [x["to"] for x in dfJoin.salary if x != None]
    cur = [x["currency"] for x in dfJoin.salary if x != None]

    # descr = [x["requirement"] for x in VacDescription]
    # VD = {"Description": descr}
    # VD_DF = pd.DataFrame(VD)

    d = {"from": frm, "to": to, "currency": cur}
    ddf = pd.DataFrame(d)

    print("4 step")

    dfVacNameWPrice = pd.concat([df_names, ddf], axis=1)
    dfVacNameWPrice = dfVacNameWPrice.fillna(0)

    print("5 step")

    currency_filter = dfVacNameWPrice["currency"] == currency
    dfVacNameWPrice = dfVacNameWPrice[currency_filter]

    fromFilter = dfVacNameWPrice["from"] > 0
    dfVacNameWPrice = dfVacNameWPrice[fromFilter]

    toFilter = dfVacNameWPrice["to"] > 0
    dfVacNameWPrice = dfVacNameWPrice[toFilter]

    print("6 step")

    # wordcloud

    from collections import Counter

    # vacancy_names = df.name
    cloud = Counter(df_names)

    from wordcloud import WordCloud, STOPWORDS

    stopwords = set(STOPWORDS)
    cloud = ""
    for x in list(df_names):
        cloud += x + " "

    wordcloud = WordCloud(
        width=800,
        height=800,
        stopwords=stopwords,
        min_font_size=8,
        background_color="white",
    ).generate(cloud)

    import matplotlib.pylab as plt

    plt.figure(figsize=(16, 16))
    plt.axis("off")
    plt.imshow(wordcloud)
    imgpath = "imgs/" + repr(datetime.datetime.now().timestamp()) + "_vacancy_cloud.png"
    plt.savefig(imgpath)

    # print(ddfc)

    priceestimate = [
        dfVacNameWPrice["from"].min(),
        dfVacNameWPrice["to"].max(),
        dfVacNameWPrice["to"].median(),
        round(dfVacNameWPrice["to"].mean(), 1),
        imgpath,
        dfVacNameWPrice,
    ]

    return priceestimate


if __name__ == "__main__":
    GetPositionSalaryEstimate("'секретарь'", "RUR")
