import requests 
import pandas as pd

# this .py file is for development and testing of lines of code

# most recent- restcountries data formatting
r = requests.get("https://restcountries.com/v3.1/name/France?fields=name,capital,currencies,languages,car")
response = r.json()

for i in response[0]['currencies'].items():
     currency_list = []
     currency_list.append(i[1]['name'])

for i in response[0]['languages'].items():
     lang_list = []
     lang_list.append(i[1])

df = pd.DataFrame(data={
     "name": response[0]['name']['common'],
     "currencies": currency_list[0],
     "capital": response[0]['capital'],
     "languages": lang_list[0],
     'car': response[0]['car']['side']})

for i in df.itertuples():
     print(i[4])