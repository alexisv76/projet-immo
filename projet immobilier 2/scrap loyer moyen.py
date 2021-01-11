# -*- coding: utf-8 -*-
"""
Created on Wed Sep 23 11:04:31 2020

@author: DIGIFAB
"""
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from bs4 import BeautifulSoup
from orm_peewee import db, Ville

retire = "-²/"
arret = ",."
adresse = ("https://www.seloger.com/prix-de-l-immo/location/haute-normandie/seine-maritime/le-havre/760351.htm")

def recuperation_nombre(x):
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
def recuperation_loyer(liste_ville):     
    driver_path = 'D:\Desktop\stageprojetimmobilier\Projet immobilier\chromedriver.exe'
    driver = webdriver.Chrome(driver_path)
    driver.get("https://www.seloger.com/prix-de-l-immo/location/haute-normandie/seine-maritime/le-havre/760351.htm")
    for ville in liste_ville :  
        try :
            
            inputs = driver.find_element_by_xpath("/html/body/div[2]/div/div[1]/div/div/div[1]/div/input")
            time.sleep(2)
            for i in range(0,100) :
                inputs.send_keys(Keys.BACK_SPACE)
            time.sleep(2)
        except :
            driver.get("https://www.seloger.com/prix-de-l-immo/location/haute-normandie/seine-maritime/le-havre/760351.htm")
            time.sleep(5)
            pass
        try :                   
            inputs.send_keys(ville.nom)
            time.sleep(2)
            inputs.send_keys(Keys.ARROW_DOWN)
            time.sleep(2)
            inputs.send_keys(Keys.ENTER)
            time.sleep(3)            
            inputs.send_keys(Keys.ENTER)
            time.sleep(3)
                     
            soup = BeautifulSoup(driver.page_source,'html.parser')
            loyer_m = soup.findAll("div",class_="sc-brqgnP fKKJCG")
            try : 
                appartement = int(recuperation_nombre(loyer_m[0].text.strip()))
                print(appartement)
                ville.loyer_moyen_appart = appartement
                ville.save()
            except:
                print(appartement,"dans except")
                pass
            # try :
            #     maison = int(recuperation_nombre(loyer_m[1].text.strip()))
            #     ville.loyer_moyen_maison = maison
            #     ville.save()
            # except : 
            #     pass
        except Exception as e:
            print("pas trouvé")
            pass
        
     
liste_ville = recuperation_ville()
recuperation_loyer(liste_ville)