# -*- coding: utf-8 -*-
"""
Created on Fri Sep 25 11:13:52 2020

@author: DIGIFAB
"""

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from bs4 import BeautifulSoup
from orm_peewee import db, Ville, Proximité, lignes

retire = "-²/"
arret = ",."
adresse = ("https://www.seloger.com/prix-de-l-immo/location/"+
           "haute-normandie/seine-maritime/le-havre/760351.htm")

def nombre(x):
    a = ""
    for i in retire:
        x = x.replace(i, " ")
    for i, mot in enumerate(x.split()):
        if mot[0].isdecimal() == True:
            for j in mot:
                if j.isdecimal() == True:
                    a += j
                if j in arret:
                    break
        else:
            if a != "":
                break
    x = a
    if x.isdecimal() == False:
        x = None
    return x


def recuperation_ville():
    villes = Ville.select()
    return villes


def recup_voisinage(liste_ville):     
    driver = webdriver.Chrome(lignes[5].strip())
    driver.get(adresse)
    liste_dico = []
    for ville in liste_ville :         
        try :            
            inputs = driver.find_element_by_xpath(
                "/html/body/div[2]/div/div[1]/div/div/div[1]/div/input")
            time.sleep(2)
            for i in range(0,100) :
                inputs.send_keys(Keys.BACK_SPACE)
            time.sleep(2)
        except :
            driver.get(adresse)
            time.sleep(5)
            pass
        try:                   
            inputs.send_keys(ville.nom)
            time.sleep(2)
            inputs.send_keys(Keys.ARROW_DOWN)
            time.sleep(2)
            inputs.send_keys(Keys.ENTER)
            time.sleep(3)            
            inputs.send_keys(Keys.ENTER)
            time.sleep(3)
                                
            soup = BeautifulSoup(driver.page_source,'html.parser')    
            dic = {}
            habitants = soup.findAll("div",class_="sc-cpmLhU kxoMnq")
            services = soup.findAll("div",class_="sc-kUaPvJ lfMIdi")
            moins_25 = soup.findAll("div",class_="sc-jzgbtB sc-TFwJa gpvaua")
                       
            dic["id_ville"] = ville.id_ville            
            dic["nombre_habitant"] = int(nombre(habitants[0].text.strip()))
            dic["nombre_ecole"] = int(nombre(services[1].text.strip()))
            dic["nombre_commerce"] = int(nombre(services[2].text.strip()))
            dic["moins_25ans"] = moins_25[0].text.strip()
            liste_dico += [dic]
      
        except Exception as e:
            print("pas trouvé", e)
            pass
        
    for voisinage in liste_dico:
        try:
            with db.atomic():
                Proximité.create(**voisinage)
        except Exception as e:
            print(e)
        pass
     
liste_ville = recuperation_ville()
recup_voisinage(liste_ville)