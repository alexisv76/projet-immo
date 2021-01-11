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
    adresse = ("https://www.seloger.com/prix-de-l-immo/vente/haute-normandie/seine-maritime/le-havre/760351.htm")
    adresse2 = ("https://www.seloger.com/prix-de-l-immo/location/"+
           "haute-normandie/seine-maritime/le-havre/760351.htm")
    for ville in dansville :
        dic = {}
        driver1, erreur = pages( ville, adresse)
        if erreur != "":
                continue
        try:
            soup = BeautifulSoup(driver1.page_source,'html.parser')
            prix_m = soup.findAll("div",class_="sc-hEsumM sc-cIShpX kIFIXr")
            
            prixmoyen_appart = int(nombre(prix_m[1].text.strip()))
            ville.prix_moyen_appart = prixmoyen_appart
            print("prixmoyen_appart",prixmoyen_appart)
            ville.save()
            
            prixmoyen_maison = int(nombre(prix_m[0].text.strip()))
            ville.prix_moyen_maison = prixmoyen_maison
            print("prixmoyen_maison",prixmoyen_maison)
            ville.save()
        except:
            print("dans except")
            pass
        
        driver1.close()
        dic = {}        
        driver2, erreur = pages(ville, adresse2)
        
        if erreur != "":
            continue
        try :
            soup = BeautifulSoup(driver2.page_source,'html.parser')
            loyer_m = soup.findAll("div",class_=
                                   "sc-hEsumM sc-cIShpX kIFIXr")           
            loyer_appart = int(nombre(loyer_m[1].text.strip()))
            ville.loyer_moyen_appart = loyer_appart
            print("loyer_appart",loyer_appart)            
            ville.save()
                    
            loyer_maison = int(nombre(loyer_m[0].text.strip()))
            ville.loyer_moyen_maison = loyer_maison
            print("loyer_maison",loyer_maison)
            ville.save()
        except :
            print("soup")
            pass
        
        try :
            habitants = soup.findAll("div",class_="sc-cpmLhU kxoMnq")
            print(habitants)
            services = soup.findAll("div",class_="sc-kUaPvJ lfMIdi")
            moins_25 = soup.findAll("div",class_="sc-jzgbtB sc-TFwJa gpvaua")
            
            dic["id_ville"] = ville.id_ville            
            dic["nombre_ecole"] = services[1].text.strip()
            dic["nombre_habitant"] = habitants[0].text.strip()
            dic["moins_25ans"] = moins_25[0].text.strip()
            dic["nombre_commerce"] = services[2].text.strip()
        except:
              print("dic")
              pass
        try:
             with db.atomic():
                 Proximite.create(**dic)
        except Exception as e:
             print(e)
             pass
        driver2.close()
        

def recup_coord(villes):
    geolocator = Nominatim(user_agent = "x")
   
    for ville in villes:
        try:
            lieu = geolocator.geocode(ville.nom)
            Coordonnees.create(id_ville=ville.id_ville, x=lieu.latitude, 
                               y= lieu.longitude)
        except:
            continue
                           
       
    
                 
              
                    
                    
                
                
        
        
        