from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import pymongo

app= Flask(__name__)

class scrape_all:

    def __init__(self):
        self.all = []
        self.all2 = []

    def search(self, entr):
        self.n = entr
        #a = int(input("enter page no"))
        a=1
        # self.mongo_connect()
        for i in range(a):
            if " " in self.n:
                print("scraping" + self.n)
                self.n = self.n.replace(' ', '%20')
            r = requests.get(f"https://www.flipkart.com/search?q={self.n}&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=on&as=off&page={a}")
            self.page = bs(r.text, 'html.parser')
            self.prod()
            # self.monput()
        self.result()
        #self.dataset()

    def prod(self):
        product = self.page.find_all('a', attrs={'class': '_1fQZEK'})
        for one_prod in product:
            self.one_product = one_prod
            self.pull_name()
            self.pull_cost()
            self.pull_rvw()
            self.pull_rating()
            self.pull_specs()
            self.pull_img()
            self.all.append((self.name, self.cost, self.specs, self.rvw, self.rating, self.img))
            self.dict={"Name":self.name,"Cost":self.cost,"Specs":self.specs,"Review":self.rvw,"Rating":self.rating}
            self.all2.append(self.dict)

    def result(self):
        try:
            return render_template('results.html',reviews=self.all2)
        except:
            return "Something's wrong"


    def dataset(self):
        df = pd.DataFrame(self.all, columns=['name', 'cost', 'specs', 'review', 'rating', 'image'])
        # df = pd.DataFrame(self.all,columns=['name','cost','review','rating'])
        #x = input("enter csv file name")
        df.to_csv((self.n + '.csv'), index=False, encoding='utf-8')
        return df

    def pull_img(self):
        try:
            self.img = self.one_product.find('img')['src']
        except:
            self.img = 'NAN'

    def pull_name(self):
        try:
            self.name = self.one_product.find('img')['alt']
        except:
            self.name = 'NAN'

    def pull_rvw(self):
        try:
            self.rvw = self.one_product.find('span', attrs={'class': '_2_R_DZ'}).text.split('\xa0&\xa0')[1]
        except:
            self.rvw = 'NAN'

    def pull_rating(self):
        try:
            self.rating = self.one_product.find('span', attrs={'class': '_2_R_DZ'}).text.split('\xa0&\xa0')[0]
        except:
            self.rating = 'NAN'

    def pull_cost(self):
        try:
            self.cost = self.one_product.find('div', attrs={'class': '_30jeq3 _1_WHN1'}).text
        except:
            self.cost = 'NAN'

    def pull_specs(self):
        try:
            self.specs = []
            for one in (self.one_product.find('ul', attrs={'class': '_1xgFaf'}).contents):
                self.specs.append(one.text)
        except:
            self.specs = 'NAN'

    def mongo_connect(self):
        client= pymongo.MongoClient("")
        db= client.mongo
        x=input("database name")
        db1=client[x]
        self.coll=db1[self.n]


    def monput(self):
        rec= {'name': self.name,
               'cost': self.cost,
                'specs':  self.specs,
                'review': self.rvw,
                'rating': self.rating,
                'image': self.img
                     }
        self.coll.insert_one(rec)

@app.route('/scrap',methods=['POST'])
def run():
    search= request.form['content'].replace(" "," ")
    scrape_all().search(search)


@app.route('/',methods=['GET'])
def home_page():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(port=8000, debug=True)