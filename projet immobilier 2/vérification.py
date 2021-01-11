from bs4 import BeautifulSoup
import requests
import urllib.request
from urllib.request import urlopen
from peewee_immo import db,Logement
import random
import time


def verification():
    liens_verif = Logement.select()
    liens_verif = random.choices(liens_verif,k=10)
    
    for lien in liens_verif:
        url = lien.lien
        reponse =  requests.get(url)
        if reponse.status_code == 404:
            q = Logement.delete().where(Logement.id_logement == lien.id_logement)
            q.execute()
            print("1 suppression")
            time.sleep(3)
        else:
            time.sleep(3)
            pass