<<<<<<< Updated upstream
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 23 14:17:17 2020

@author: alexis
"""


=======
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 21 14:50:06 2020

@author: DIGIFAB
"""

>>>>>>> Stashed changes
from bs4 import BeautifulSoup
import requests
import urllib.request
from urllib.request import urlopen
<<<<<<< Updated upstream
from peewee_immo import db,Logement
=======
from orm_peewee import db,Logement
>>>>>>> Stashed changes
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
<<<<<<< Updated upstream
        
=======
>>>>>>> Stashed changes
