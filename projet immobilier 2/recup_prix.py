#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct  5 10:58:03 2020

@author: alexis
"""
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from orm_peewee import db, Ville, Proximite,Coordonnees
from geopy.geocoders import Nominatim

def nombre(x):
    a = ""
    for i in "-²/":
        x = x.replace(i, " ")
    for i, mot in enumerate(x.split()):
        if mot[0].isdecimal() == True:
            for j in mot:
                if j.isdecimal() == True:
                    a += j
                if j in ",.":
                    break
        else:
            if a != "":
                break
    x = a
    if x.isdecimal() == False:
        x = None
    return x

def pages(ville,adresse):
    driver = webdriver.Chrome('C:/Users/vauch/Desktop/projet immobilier 2/chromedriver')
    #driver = webdriver.Chrome(lignes[5].strip())
    driver.get(adresse)
    
    try :
        erreur = ""
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
    try : 
        print(ville.nom,ville)
        inputs.send_keys(ville.nom)
        time.sleep(2)
        inputs.send_keys(Keys.ARROW_DOWN)
        time.sleep(2)
        inputs.send_keys(Keys.ENTER)
        time.sleep(3)            
        inputs.send_keys(Keys.ENTER)
        time.sleep(3)
        
    except :
        erreur = "pas adresse"
        print(erreur)
        pass         
    return driver, erreur     

def recuperation_proxi(dansville):
    adresse = ("https://www.meilleursagents.com/prix-immobilier/rouen-76000/")
    driver = webdriver.Chrome('C:/Users/vauch/Desktop/projet immobilier 2/chromedriver')
    #driver = webdriver.Chrome(lignes[5].strip())
    driver.get(adresse)
    for ville in dansville :
        try :
            erreur = ""
            inputs = driver.find_element_by_xpath(
                "/html/body/div[2]/div[3]/div[1]/span/input[2]")
            time.sleep(2)
            for i in range(0,100) :
                inputs.send_keys(Keys.BACK_SPACE)
            time.sleep(2)
        except :
            driver.get(adresse)
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
            
        except :
            erreur = "pas adresse"
            driver.close()
            adresse = ("https://www.meilleursagents.com/prix-immobilier/rouen-76000/")
            driver = webdriver.Chrome('C:/Users/vauch/Desktop/projet immobilier 2/chromedriver')
            driver.get(adresse)
            print(erreur)
            pass  
        
        if erreur != "":
            continue
        
        try :
            soup = BeautifulSoup(driver.page_source,'html.parser')
            prix_m = soup.findAll("li",class_="big-number")
            
            if len(prix_m) > 2 :
                prixmoyen_appart = int(nombre(prix_m[0].text.strip()))
                ville.prix_moyen_appart = prixmoyen_appart
                print("prixmoyen_appart",prixmoyen_appart)
                ville.save()
                
                prixmoyen_maison = int(nombre(prix_m[1].text.strip()))
                ville.prix_moyen_maison = prixmoyen_maison
                print("prixmoyen_maison",prixmoyen_maison)
                ville.save()
                
                loyer_appart = int(nombre(prix_m[2].text.strip()))
                ville.loyer_moyen_appart = loyer_appart
                print("loyer_appart",loyer_appart)            
                ville.save()
                
                loyer_maison = int(nombre(prix_m[2].text.strip()))
                ville.loyer_moyen_maison = loyer_maison
                print("loyer_maison",loyer_maison)
                ville.save()
                
            else: 
                prixmoyen_appart = int(nombre(prix_m[0].text.strip()))
                ville.prix_moyen_appart = prixmoyen_appart
                print("prixmoyen_appart",prixmoyen_appart)
                ville.save()
                
                loyer_appart = int(nombre(prix_m[1].text.strip()))
                ville.loyer_moyen_appart = loyer_appart
                print("loyer_appart",loyer_appart)            
                ville.save()
                
                loyer_maison = int(nombre(prix_m[1].text.strip()))
                ville.loyer_moyen_maison = loyer_maison
                print("loyer_maison",loyer_maison)
                ville.save()
            
        except :
            pass
        
def recup_coord(villes):
    geolocator = Nominatim(user_agent = "x")
   
    for ville in villes:
        try:
            lieu = geolocator.geocode(ville.nom)
            Coordonnees.create(id_ville=ville.id_ville, x=lieu.latitude, 
                               y= lieu.longitude)
        except:
            continue
            