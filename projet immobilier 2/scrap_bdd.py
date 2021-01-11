#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Introduction: ce programme a été conçu pour recupérer et stocker des
données de biens immobiliers a renover en Normandie pour un client potentiel
avec les critères qu'il aura défini au préalable.
Le but final est de développer une application qui permettra à l'utilisateur de
visualiser et de rechercher des biens selon ses choix.

methode
lire le contenu des pages web
utilisation de la methode scrap grace au module BeautifulSoup
on recupere les liens pour lire les pages, on controle si les liens
contiennent les biens
recuperation du contenu des pages html
analyse de la structure, examiner les balises des contenus 
qui nous interressent, on utilise l'instruction inspecter dans le navigateur
appliquer la methode soup sur les balises
recuperer le texte contenant les données
nettoyer les données 
affiner l'extraction avec l'instruction find 
traiter les données pour obtenir un texte ou un nombre si c est le cas
effectuer les operations necesaires
ranger les données dans un dictionnaire
creer une base de données avec la liste de dictionnaires
les clés seront les colonnes et les valeurs seront les lignes

partie traitement:
plusieurs posibilités suivant le type de balises choisies
exemple :balise tb avec l'instruction find_all contient plus de valeurs ,
il faudra chercher le contenu à l'aide d'une boucle for et comparer
le texte cherché à celui trouvé
il sera possible d'utiliser l'instruction split afin de separer 
le texte en mot pour recuperer les mots uniquement necessaires

les balise exemple h1 permettent une recuperation aprés un nettoyage 
ou avec un split on selectionnera l'element

les balises avec classe permettent avec l'instruction .text 
de recuperer le texte qui suit la classe

Created on Wed Jul  8 16:19:15 2020
@author: Sabrina
"""

import matplotlib.pyplot as plt
import psycopg2
from sqlalchemy import create_engine
import time
import pandas as pd
import random
import datetime
import time
from sqlalchemy import MetaData
from sqlalchemy import create_engine
from orm_peewee import Ville, Logement, db, Types_bien, Utilisateurs
from bs4 import BeautifulSoup
from urllib.request import urlopen
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from apscheduler.schedulers.background import BackgroundScheduler
from prix_moyen import recuperation_prix2


dico_types = {"appartement":1, "immeuble":2, "maison":3}
# for keys,value in dico_types.items():
#     Types_bien.create(type_bien = keys)

dico_super = [{"lien":
                 "https://www.superimmo.com/achat/immeuble/haute-"+
                 "normandie,basse-normandie/a-renover","nombre":3},
               {"lien":"https://www.superimmo.com/achat/haute-"+
                "normandie,basse-normandie/a-renover","nombre":3}]

# recuperer les liens contenu dans les balises (a)
def liens_super(dico_super):
    debut = time.time()
    liens_recherche = []
    for dico in dico_super:        
        for page in range(1, dico["nombre"] + 1):
            for url in [dico["lien"]+ "/p/" + str(page)]:
                html = urlopen(url)
                soup = BeautifulSoup(html, "html.parser")
                time.sleep(random.randint(10, 15))
                liens = soup.find_all("a")
            # mettre dans une liste les liens si ils contiennent un bien 
                for lien in liens:
                    try:
                        lien = lien["href"]
                        deblien = "https://www.superimmo.com"
                        if deblien + lien not in liens_recherche:                                       
                            for x in sorted(dico_types):
                                if x in lien:
                                    liens_recherche += [deblien + lien]
                    except:
                        pass
    fin = time.time()
    performance1 = [fin-debut]
    print("la fonction lien_super a été executée en" , performance1)
    return liens_recherche, performance1

def abc(dico, dico_super):    
    liens_recherche = []
    dimension_liens = 0
    for dico in dico_super:        
        for page in range(1, dico["nombre"] + 1):
            for url in [dico["lien"]+ "/p/" + str(page)]:
                html = urlopen(url)
                soup = BeautifulSoup(html, "html.parser")
                time.sleep(random.randint(10, 15))
                liens = soup.find_all("a")
            # mettre dans une liste les liens si ils contiennent un bien 
                for lien in liens:
                    try:
                        lien = lien["href"]
                        deblien = "https://www.superimmo.com"
                        if deblien + lien not in liens_recherche:                                       
                            for x in sorted(dico_types):
                                if x in lien:
                                    dimension_liens += 1
                                    liens_recherche += [deblien + lien]
                    except:
                        pass
    return liens_recherche, dimension_liens
                    
def liens_super2(dico_super):
    debut = time.time()                    
    for dico in dico_super:
        liens_recherche, dimension_liens = abc(dico, dico_super)                
    fin = time.time()
    performance2 = [fin-debut]
    print("Nombre de liens recherchés au total", dimension_liens)
    print("La fonction lien_super2 a été executée en " , performance2)
    return dimension_liens, performance2


def graph_performance(dimension_liens, performance1, performance2):
    """ Génération d'un graphique de comparaison des performances"""
    plt.plot(dimension_liens, performance1, '-o')
    plt.plot(dimension_liens, performance2, '-x')
    plt.legend(['Performance 1', 'Performance 2'],loc = 'upper left')
    plt.xlabel("Nombre de liens au total")
    plt.ylabel("Performance")
    plt.title("Performance de scraping de liens")
    plt.savefig("Performances.png")
    plt.show()


# extraire les nombres à l'interieur d'un texte
def recup_nombre(x, pp, NC):
    a = ""
    for j in str(x):
        if j in pp:
            break
        if j in "0123456789":
            a += j
    if len(a) < 1:
        a = NC
    return a


def recuperation_superimmo(liens_recherche):
    """ Fonction qui parcoure la liste de liens,scrape et nettoie les données
    des biens"""    

    driver_path = 'D:\Desktop\stageprojetimmobilier\Projet immobilier\chromedriver.exe'
    driver = webdriver.Chrome(driver_path)
    liste_dico = []
    for lien in liens_recherche:              
        driver.get(lien)               
        try:        
            search = driver.find_element_by_class_name("display-phone-number")
            search.send_keys("enter")    
            search.send_keys(Keys.RETURN)
        except: 
            pass
        time.sleep(random.randint(3, 6))
        if "annonces" not in lien:
            continue
        # lecture des pages sources
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # bloc de recuperation des données par l'intermediaire de balises
        # pour la constitution d'une base de données
        # adresse et code postal
        dic = {} 
        lieux = soup.find_all('span', class_='location')
        dic["cp"] = recup_nombre(lieux[0], "", "NC")
        adresse = lieux[0].text.strip().replace("\n", "(").replace("'", " ")
        dic["lieu"] = adresse[adresse.find(adresse[0]) : adresse.find("(")]
   
        # surface et id_type
        surfaces = soup.find_all("h1")
        surfaces = surfaces[0].text.strip().split()
        dic["surface"] = int(recup_nombre(surfaces[2], ".,", "0"))
        dic["id_type"] = 0
        if surfaces[1] in dico_types:
            dic["id_type"] = dico_types[surfaces[1]]
         
        # date de creation et date de publication
        dic["date_crea"] = datetime.datetime.today().strftime('%d-%m-%Y')
        dic["date_publi"] = dic["date_crea"]
        dates = soup.find_all("small")
        dates = dates[1].text.strip().split()
        dates = dates[2].replace("/", "")
        if len(dates) > 6:
            dates = datetime.datetime.strptime(dates, "%d%m%Y").date()
            dic["date_publi"] = dates
        
        # numero de telephone
        dic["contact"] = "NC"
        telephone = soup.find("div", class_="call-text phone")
        if telephone != None and len(telephone.text.strip()) > 7:
            dic["contact"] = telephone.text.strip()
        
        # prix du bien
        prix = soup.find_all('b', class_='price')
        prix = prix[0].text.strip()
        dic["prix"] = float(recup_nombre(prix, ".,", "0"))
        
        # calcul du prix du metre carré
        dic["prix_metre_carre"] = 0
        if dic["surface"] > 0:
            dic["prix_metre_carre"] = round(dic["prix"]/dic["surface"])

        # taxe_fonciere et année de construction    
        dic["taxe_fonciere"] = "NC"
        dic["annee"] = "NC"
        cellules = soup.find_all("td")
        for infos in cellules:
            infos = infos.text.strip()
            if "fonci" in infos:
                dic["taxe_fonciere"] = recup_nombre(infos, "", "NC")
            if "Année de construction" in infos:
                dic["annee"] = recup_nombre(infos, "", "NC")
         
        # dpe et classe energie
        dic["dpe"] = "NC"
        dic["energie"] = "NC"
        dpe_energie = soup.find("span", class_="label")
        if dpe_energie != None:
            dpe_energie = dpe_energie.text.strip()
            if len(str(dpe_energie)) > 4:
                dic["dpe"] = dpe_energie[:-1]
                dic["energie"] = dpe_energie[-1]
            if len(str(dpe_energie)) == 1:            
                dic["energie"] = dpe_energie
        
        # description du bien et indication si centre ville
        dic["quartier"] = "NC"
        dic["description"] = "NC"
        descriptions = soup.find("p", "description")
        if descriptions != None:
            dic["description"] = descriptions.text.strip()
            if "centre" in dic["description"]:
                dic["quartier"] = "centre ville"
        dic["lien"] = lien
        
        # creer une liste qui contient un ensemble de dictionnaires de données
        liste_dico += [dic]
    driver.close
    return liste_dico


def insert_bien(liste_dico):
    """Insertion des données scrapées dans la base de données"""
    
    # recuperation des données contenues dans la table ville
    debut = time.time()
    liste_ville = []
    for v in Ville.select():
        liste_ville += [v.nom]
    nb = 0             
    nouvelle_villes = []
    for ddico in liste_dico:
        if ddico["lieu"] not in liste_ville:
            liste_ville.append(ddico["lieu"]) 
            num_ville = Ville.create(nom = ddico["lieu"])
            nouvelle_villes.append(num_ville)
        else:
            recuperateur = Ville.select().where(Ville.nom == ddico["lieu"])
            for r in recuperateur:
                num_ville = r
        liste_dico[nb]["id_ville"] = num_ville.id_ville
        nb += 1 
            
    #creations des données dans la base grâce aux dictionnaire.id_ville
    for biens in liste_dico: 
        try:     
            with db.atomic():
                Logement.create(**biens)
        except Exception as e:
            print(e)
            pass
    fin = time.time()
    performance_insert = [fin-debut]
    print("la fonction insert_bien a été executée en" , performance_insert)
    return nouvelle_villes

def test_doublons():
    # connexion - supprime tables si existes - copie de Logement
    engine = create_engine(
        'postgresql://postgres:digifab@127.0.0.1:5432/postgres')
    engine.execute('drop table if exists table_sans_doublons;')
    copie = pd.read_sql_query("select * from logement;", engine)
    
    # supprime elements doubles, et crée (table_sans_doublons)
    copie = copie.drop_duplicates(subset=['surface'])
    copie.to_sql('table_sans_doublons', engine, index=False)
    
    # voir les tables créées
    m = MetaData()
    m.reflect(engine)
    for table in m.tables.values():
        print("table:", table)
    return 

# lancement du programme
if __name__ == '__main__':
    recup_liens = False
    recup_liens2 = False
    graphique = False
    scrap_donnees = False
    insertion_donnees = False
    doublons = False
    
     
    if recup_liens:                                              
        liens_recherche, performance1 = liens_super(dico_super)  
    
    if recup_liens2:    
        dimension_liens, performance2 = liens_super2(dico_super) 
    
    if graphique:       
        graph_performance(dimension_liens, performance1, performance2)   
        
    if scrap_donnees:    
        liste_dico = recuperation_superimmo(liens_recherche)
        
    if insertion_donnees:
        nouvelle_villes = insert_bien(liste_dico)
        try:            
            recuperation_prix2(nouvelle_villes)
        except:
            pass
    
    if doublons:    
        test_doublons()
