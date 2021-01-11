#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Introduction: ce programme a été conçu pour recupérer et stocker des 
données de biens immobiliers a renover en Normandie pour un client potentiel 
avec les critères qu'il aura défini au préalable. 
Le but final est de développer une application qui permettra à l'utilisateur de
visualiser et de rechercher des biens selon ses choix.


Created on Wed Jul  8 16:19:15 2020

@author: Sabrina
"""

from bs4 import BeautifulSoup
import requests
import urllib.request
from urllib.request import urlopen
from fake_useragent import UserAgent
import itertools as it
import random
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from orm_peewee import Ville, Logement, db, Types_bien
import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import recup_prix

liste_dpe = {"label a":"A","label b":"B","label c":"C","label d":"D",
            "label e":"E","label f":"F","label g":"G"}
liste_energie = {"label label-t2 a":"A","label label-t2 b":"B",
                "label label-t2 c":"C","label label-t2 d":"D",
                "label label-t2 e":"E","label label-t2 f":"F",
                "label label-t2 g":"G"}

dico_types = {"appartement":1,"immeuble":2,"maison":3}

#il faut remplacer les valeurs par celle de la base

#for keys,value in dico_types.items() :
    #Types_bien.create(type_bien = keys)
  
def obtention_url(dico_liens,connecteur):
    liens_scrapp = []    
    for dico in dico_liens :        
        liens_scrapp += [dico["lien"]]
        for page in  range(2,dico["nombre"]+1):
            liens_scrapp += [dico["lien"]+connecteur+str(page)]  
    return liens_scrapp

def liens_super(urls):
    liens_recherche = []
    for url1 in urls :
        url = url1
        html = urlopen(url)
        soup = BeautifulSoup(html,"html.parser")
        time.sleep(random.randint(10,15))
        liens = soup.find_all("a")
        for lien in liens:
            try:
                lien = lien["href"]
                if "https://www.superimmo.com"+lien not in liens_recherche:                                        
                    if ("maison" in lien  or "appartement" in lien  or
                        "immeuble" in lien  ):
                        print(lien)
                        liens_recherche += ["https://www.superimmo.com"+lien]                   
            except:
                pass
    return liens_recherche


def recuperation_superimmo(liens_recherche):
    """ liens_recherche est la liste de liens que le programme doit parcourir """    
    download_path = "C:/Users/vauch/Desktop/projet immobilier 2/static/img"
    print(len(liens_recherche))
    liste_donnees = []
    driver_path = 'C:/Users/vauch/Desktop/projet immobilier 2/chromedriver'
    driver = webdriver.Chrome(driver_path)
    for lien in liens_recherche :               
        driver.get(lien)
        try:        
            search = driver.find_element_by_class_name("display-phone-number")
            search.send_keys("enter")    
            search.send_keys(Keys.RETURN)
        except: 
            pass        
        time.sleep(random.randint(3, 6))
        
        
    
        try:         
            soup = BeautifulSoup(driver.page_source,'html.parser')
            phone = soup.find("div",class_="call-text phone").text.strip()            
            prix = soup.find_all('b',class_='price')
            prix = prix[0].text.strip()
            liste_prix = []
            
            #telechargement des images
  
            
            infos = soup.find("h1")
            infos = infos.text.strip().split("-")
            for info in infos:
                if "ter." in info:
                    info = info.split("\n")
                    surface_terrain = info[0][1:-1]
                else:
                    surface_terrain = "non"
                if "chambre" in info:
                    info = info[1:-1].split(" ")
                    chambre = info[0]
                else:
                    chambre = 0
                
               
                    
                
            for p in prix:
                try:
                    p = int(p)
                    liste_prix += [str(p)]                   
                except:
                    pass
            prix2 = "".join(liste_prix[:])
            
           
            metre_carre = soup.find_all("small", class_="price_square")
            metre_carre = metre_carre[0].text.strip()
            localisation = soup.find_all('span', class_='location')            
            n = 0
            for l in localisation[0].text.strip():
                n += 1
                if l == "(":
                    p1 = n
                if l == ")":
                    p2 = n            
            ville = localisation[0].text.strip()[:p1-1] 
            if ville == None:
                ville = "NC"
            code_postal = localisation[0].text.strip()[p1:p2-1]            
            datep = soup.find_all("small")
            datep = datep[1].text.strip().replace("\n","%")            
            liste = []
            e = 0
            for d in datep:
                e+=1
                if d == "%":
                    p1 = e
                    liste += [p1] 
                    
            le = datep.find("le")
            datep = datep[le+2:liste[0]-1]            
            description = soup.find_all("p",class_="description")
            description = description[0].text.strip()
            b = "centre ville" in description
            if b == True :
                quartier = "centre ville"
            else :
                quartier = ""
            
            if "balcon"  in description or "terrasse" in description:
                ext = "oui"
            else:
                ext = "non"
            
            if "parking" in description or "garage" in description:
                place = "oui"
            else:
                place = "non"
            
            if "cave" in description:
                cave = "oui"
            else:
                cave = "non"
                
            liste_dpes = []
            dpe = ''
            for classe,valeur in liste_dpe.items() :            
                dpe_ = soup.find_all("span", class_=classe)
                liste_dpes += [dpe_]
            for liste_d in liste_dpes :
                if len(liste_d)>0:
                    dpe_ = liste_d
            
            if dpe_ != []:
                dpe = dpe_[0].find("b").text.strip()
                    
            liste_nrj = []
            energie = ''        
            for classe_e,valeur_e in liste_energie.items() :
                energie_ = soup.find_all("span", class_=classe_e)
                liste_nrj += [energie_]
            for liste in liste_nrj:                
                if len(liste) > 0:
                    energie_ = liste                                
            if energie_ != []:
                energie = energie_[0].find("b").text.strip()
                
            cellules = soup.find_all("td")
            taxe_f = 'NC'
            annee = 'NC'
            for infos in cellules:                
                # if "e de construction" in infos.text.strip():                    
                #     annee = infos.text.strip()   
                # if len(annee) < 4:
                #     annee = "NC"
                if "fonci" in infos.text.strip():
                    taxe_f = infos.text.strip()
                            
            immeuble = False
            immeuble = "immeuble" in lien 
            if immeuble == True:
                id_type = dico_types["immeuble"]
            
            appartement = False
            appartement = "appartement" in lien
            if appartement == True:                
                id_type = dico_types["appartement"]
            
            maison = False    
            maison = "maison" in lien
            if maison == True :
                id_type = dico_types["maison"]  
                
            img_url = soup.find_all("a",class_="fancybox")[0]["href"]
            req = urllib.request.Request(img_url)
            raw_img = urllib.request.urlopen(req).read()
            nom_image = (download_path+"/"+"image"+lien.replace(".","_").replace(
            "/","_").replace(":","_")+".jpg")
            f = open(nom_image,"wb")
            f.write(raw_img)
            f.close()
                

    
            
            liste_donnees += [{"id_type":id_type,"prix":prix2,
                             "prix_metre":metre_carre,
                             "ville":ville,"cp":code_postal,"date":datep,
                             "quartier":quartier,"dpe":dpe,"energie":energie,
                             "description":description,"lien":lien,
                             "annee":annee,"taxe_f":taxe_f,"contact":phone,
                             "nb_chambre":chambre,"surface_t":surface_terrain,
                             "cave":cave,"place":place,"ext":ext}]
        except Exception as e:
            print("error", e)            
    driver.close       
    
    return liste_donnees

    
def controle(x):
    a = []
    x = x.replace("-", " ")
    x = x.replace("²", " ")
    for i, elt in enumerate(x.split()):
        if elt[0].isdigit() == True:
            for j in elt:
                if j.isdigit() == True:
                    a += j
                if j == "," or j == ".":
                    break
    x = "".join(a)
    if not x.isdigit() == True:
        x = None
    return x

def calcul(x, y):
    if x.isdigit() == False:x = controle(x)
    if y.isdigit() == False:y = controle(y)
    m = None
    if x != None and y != None:
        if len(list(str(x))) > 7 :
            x = list(str(x))
            x[-2:-2] = "."
            x = "".join(x)
        m = round(float(x)/int(y))
    print(x, y, m)
    return x, y, m

def insert_bien(liste_dico):
   
    liste_ville = []
    nouvelle_villes = []
    
    #recuperation des donnees contenues dans la tables villes
    query = Ville.select()
    for v in query :
        if v.nom not in liste_ville: 
            liste_ville += [v.nom]
    
    for d in liste_dico:
        
        try :  
            
            prix, prix_metre_carre, surface = calcul(d["prix"],
                                            d["prix_metre"])
            if prix != None:
                prix = float(prix)  
            else:
                prix = 0     
            if prix_metre_carre != None:
                prix_m = prix_metre_carre 
            else:
                prix_m = 0    
            if surface != None:
                surface = int(surface) 
            else:
                surface = 0
            
            if d["ville"][-1] == " ":
                ville = d["ville"][:-1]
            else :
                 ville = d["ville"]
            
            ville = ville.replace("'"," ")
            
            if ville not in liste_ville:
                liste_ville += [ville]
                nouvelle_ville = Ville.create(nom = ville)
                #la liste nouvelle_villes permet de récuperer les donnees 
                #de cette ville par la suite
                nouvelle_villes += [nouvelle_ville]
            datep = d["date"]        
            datep = datep.replace(" ","")
            datep = datep.replace("/","")
            datep = datetime.datetime.strptime(datep, "%d%m%Y").date()
            datec = datetime.datetime.now()
            
            query = "call insert_biens('"+ville+"','"+d['cp']+"','"
            query += d['quartier']+"','"+d['dpe']+"','"+d['energie']+"','"
            query += d['description'].replace("'","?").replace("%","$")+"','"+str(d['annee'])+"','"+d['taxe_f']
            query +="','"+ d['contact']+"','"+str(datep)+"','"+d['lien']+"','"+str(prix)+"','"
            query += str(surface) +"','"+str(prix_m)+"','"+str(d['id_type'])+"','"+str(datec)+"','"
            query += str(d['nb_chambre'])+"','"+d['cave'] +"','"+d['place']+"','"+d['surface_t']
            query += "','"+d['ext']+ "')" 
            db.execute_sql(query)
            
        except Exception as error :
            
            print(error)
            pass
        
    return nouvelle_villes
    
# def insert_bien(liste_dico):
#     """mise en forme des donnees avant leurs insertions dans la base
#     exemple dico  liste_donnees = {"id_type":id_type,"prix":prix2,
#     "prix_metre":metre_carre,"ville":ville,"cp":code_postal,"date":datep,
#    "quartier":quartier,"dpe":dpe,"energie":energie,"description":description,
#    "lien":url}"""  
    
#     bien = []
#     nb_bien = 0
#     liste_ville = []
#     nouvelle_villes = []
    
#     #recuperation des donnees contenues dans la tables villes
#     query = Ville.select()
#     for v in query :
#         if v.nom not in liste_ville: 
#             liste_ville += [v.nom]
                 
#     for dico in liste_dico:
        
#         try :      
            
#             bien += [{"id_type":dico["id_type"]}]
            
#             # mise en forme des donneeses numériques
#             prix, prix_metre_carre, surface = calcul(dico["prix"],
#                                             dico["prix_metre"])
            
#             #pour chaque donneese contenue dans le dictionnaire nous verifions
#             #sa valeur puis nous l'ajoutant au dictionnaire "propre" avec une 
#             #clé possédant le même que la colonne qui lui est associé dans 
#             #la table
            
#             if prix != None:
#                 bien[nb_bien]["prix"] = float(prix)  
#             else:
#                 bien[nb_bien]["prix"] = 0     
#             if prix_metre_carre != None:
#                 bien[nb_bien]["prix_metre_carre"] = prix_metre_carre 
#             else:
#                 bien[nb_bien]["prix_metre_carre"] = 0    
#             if surface != None:
#                 bien[nb_bien]["surface"] = int(surface) 
#             else:
#                 bien[nb_bien]["surface"] = 0
            
#             if dico["ville"][-1] == " ":
#                 ville = dico["ville"][:-1]
#             else :
#                 ville = dico["ville"]
            
#             # Verifier si la ville est présente dans la table "ville" si 
#             # elle n'y est pas elle est créée
#             if ville not in liste_ville:
#                 liste_ville += [ville]
#                 nouvelle_ville = Ville.create(nom = ville)
#                 #la liste nouvelle_villes permet de récuperer les donnees 
#                 #de cette ville par la suite
#                 nouvelle_villes += [nouvelle_ville]
                
#             #si oui nous récupérons son id   
#             else :
#                 recuperateur = Ville.select().where(Ville.nom == ville)
#                 for r in recuperateur :
#                     nouvelle_ville = r
                
#             #il ne reste plus qu'a remplir le dictionnaire              
#             bien[nb_bien]["id_ville"] = nouvelle_ville.id_ville
#             bien[nb_bien]["cp"] = dico["cp"]
#             bien[nb_bien]["quartier"] = dico["quartier"]
#             bien[nb_bien]["dpe"] = dico["dpe"]
#             bien[nb_bien]["energie"] = dico["energie"]
#             bien[nb_bien]["description"] = dico["description"]
#             bien[nb_bien]["annee"] = dico["annee"]
#             bien[nb_bien]["taxe_fonciere"] = dico["taxe_f"]
#             bien[nb_bien]["contact"] = dico["contact"]
#             datep = dico["date"]        
#             datep = datep.replace(" ","")
#             datep = datep.replace("/","")
#             datep = datetime.datetime.strptime(datep, "%d%m%Y").date()
#             bien[nb_bien]["date_publi"] = datep
            
#             bien[nb_bien]["lien"] = dico["lien"]
#             bien[nb_bien]["date_crea"] = datetime.datetime.now()
#             nb_bien += 1
            
#         except Exception as error :
#             print(error)
#             pass
        
#     for biens in bien : 
#         #creations des donneeses dans la base grâce aux dictionnaire
#         try :     
#             with db.atomic() :
#                 Logement.create(**biens)
#         except Exception as e:
#             print(e)
#             pass
    
#     return nouvelle_villes



if __name__ == '__main__':
    lancement = True
    if lancement : 
        dico_super = [{"lien":
"https://www.superimmo.com/achat/immeuble/haute-normandie,basse-normandie/a"+
"-renover","nombre":3},{"lien":"https://www.superimmo.com/achat/haute-normandie"+
",basse-normandie/a-renover","nombre":3}]  
        liens_scrapp = obtention_url(dico_super,"/p/")               
        liens_recherche = liens_super(liens_scrapp)              
        liste_donnees = recuperation_superimmo(liens_recherche)
        nouvelle_villes = insert_bien(liste_donnees)
        try :
            
            recup_prix.recuperation_proxi(nouvelle_villes)
        except :
            print('erreur')
            pass
        recup_prix.recup_coord(nouvelle_villes)
    bien = Logement.select().where(Logement.image.is_null(True))
   
    for b in bien:
        b.image = "/static/img/image"+b.lien.replace(".","_").replace(
                    "/","_").replace(":","_")+".jpg"
        b.save()
        
         
       
       
        
        

