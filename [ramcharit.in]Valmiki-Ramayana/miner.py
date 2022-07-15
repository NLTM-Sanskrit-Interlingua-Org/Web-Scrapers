from fileinput import filename
import re
import requests
from bs4 import BeautifulSoup as bs
import trafilatura as trf
import pandas as pd
from tqdm import tqdm

def link_collector(link, sub_link):
    list_of_links = []
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0',
    }   # headers for the request

    r = requests.get(link, headers=headers)
    cont = r.content
    soup = bs(cont, 'html.parser')
    for link in soup.find_all('a', attrs={'href': re.compile("^"+sub_link)}):

        list_of_links.append(link.get('href'))
    list_of_links = list(set(list_of_links))
    return list_of_links

def corrector(combined_data):
    for i in range(len(combined_data)):
        if i%2 != 0:
            if len(re.findall('<lb/>',combined_data[i])) ==1:
                sentence_holder = combined_data[i].split('<lb/>')
                combined_data[i] = sentence_holder[0] 

            temp_sentence = re.sub("<lb/>","</p>\n<p>",combined_data[i],1)
            sentence_holder = temp_sentence.split('\n')
            if len(sentence_holder) == 2:
                combined_data[i] = sentence_holder[0]
                combined_data.insert(i+1,sentence_holder[1])
                break
    return combined_data


def content_miner(link, flag):
    clean_combined_data = []
    result = {}
    sanskrit = [flag]
    hindi = [flag]
    download = trf.fetch_url(link)
    xml_string = trf.extract(download, output_format="xml", include_comments=False)
    temp_combined_data = xml_string.split('\n')
    combined_data = temp_combined_data[3:]
    combined_data = corrector(combined_data)
    for i in combined_data:
        if "<p>" or "<head" in i:
            t = re.sub('<head rend="h2">', "<p>", i)
            t_ = re.sub('</head>','</p>',t)
            t1 = re.sub("<lb/>"," ", t_) # remove <lb/> from string
            t2 = re.sub("    <p>|</p>","",t1) #remove <p> and </p> from string
            clean_combined_data.append(t2)
    if len(clean_combined_data)%2 == 0:
        pass
    else:
        clean_combined_data.pop()

    for i in range(len(clean_combined_data)):
        if (i % 2) == 0:
            sanskrit.append(clean_combined_data[i])
        else:
            hindi.append(clean_combined_data[i])
    # result = {'sanskrit': 'sub_link'+'Sanskrit', 'hindi': 'sub_link'+'Hindi'}
    result = {'sanskrit': sanskrit, 'hindi': hindi}
    result_df = pd.DataFrame(result)
    
    # print(result_df.head())
    # result_df.to_csv(filename, index=False)
    return result_df

def main():
    file = pd.DataFrame(columns=['sanskrit', 'hindi'])

    links = ["https://www.ramcharit.in/valmiki-ramayana-bala-kanda-in-sanskrit-with-hindi-meaning-pdf/",
         "https://www.ramcharit.in/valmiki-ramayana-ayodhya-kand-complete-in-hindi-pdf/",
         "https://www.ramcharit.in/valmiki-ramayana-aranya-kanda-in-hindi-sanskrit-complete-pdf/",
         "https://www.ramcharit.in/valmiki-ramayana-kiskindha-kanda-in-hindi-sanskrit-complete-pdf/",
         "https://www.ramcharit.in/valmiki-ramayana-sundara-kanda-in-hindi-sanskrit-complete-pdf/",
         "https://www.ramcharit.in/valmiki-ramayana-yuddha-kanda-in-hindi-sanskrit-complete-pdf/",
         "https://www.ramcharit.in/valmiki-ramayana-uttar-kanda-in-hindi-sanskrit-complete-pdf/"
]


    sub_links= ["https://www.ramcharit.in/valmiki-ramayana-balakanda",
          "https://www.ramcharit.in/valmiki-ramayana-ayodhyakanda",
          "https://www.ramcharit.in/valmiki-ramayana-aranyakanda",
          "https://www.ramcharit.in/valmiki-ramayana-kiskindhakand",
          "https://www.ramcharit.in/valmiki-ramayana-sundarakanda",
          "https://www.ramcharit.in/valmiki-ramayana-yuddhakanda",
          "https://www.ramcharit.in/valmiki-ramayana-uttarkanda"
]
    filenames= ["data/chapter-1.csv","data/chapter-2.csv",
                "data/chapter-3.csv","data/chapter-4.csv",
                "data/chapter-5.csv","data/chapter-6.csv",
                "data/chapter-7.csv"]
    for i in tqdm(range(len(links))):
        # link = "https://www.ramcharit.in/valmiki-ramayana-bala-kanda-in-sanskrit-with-hindi-meaning-pdf/"
        # sub_link = "https://www.ramcharit.in/valmiki-ramayana-balakanda"
        # filename = 'Chapter-1.csv'
        list_of_links = link_collector(links[i], sub_links[i])
        # list_of_links = link_collector(link,sub_link)
        data = []
        for j in tqdm(range(len(list_of_links))):
            # print(i)
            # file.append(content_miner(i))
            # print(re.findall("[0-9]|[0-9]{2}", list_of_links[j])[0])
            if len(re.findall("[0-9]|[0-9]{2}", list_of_links[j])) == 0:
                flag = "Sarga Chapter- "+ "000"
            else:
                flag = "Sarga Chapter- "+ re.findall("[0-9]{1,2}", list_of_links[j])[0]
            data.append(content_miner(list_of_links[j], flag))

        file = pd.concat(data, ignore_index=True)
        file.to_csv(filenames[i], index=False)

if __name__ == "__main__":
    main()
