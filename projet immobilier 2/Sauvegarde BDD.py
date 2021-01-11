# -*- coding: utf-8 -*-
"""
Created on Thu Sep  3 15:58:40 2020

@author: DIGIFAB
"""
from orm_peewee import Ville, Logement, db, Types_bien, Utilisateurs
import pandas as pd
import csv
from sqlalchemy import create_engine
import datetime
from datetime import timedelta 
import sched

def sauvegarde_base_de_donnees(nom_base):
    """fonction qui va permettre de sauvegarder la base de données a la date du
    jour"""
    # listes des feuilles excel et des tables
    sheet=[]
    tb=[]
    
    # connexion db
    engine = create_engine('postgresql://postgres:digifab@127.0.0.1:5432/postgres')
    con = engine.connect()
    
    # requête sql pour récupérer toutes les tables de la db
    tables = list(con.execute("""SELECT table_name FROM information_schema.tables
                      WHERE table_schema='public'"""))
   
    # chaque table de la base de données est sauvegardée sous forme d'un 
    # fichier Excel  
    for table in tables:
        # Date actuelle 
        now = datetime.datetime.now()
        # date actuelle en chaine de carac
        str_now = now.strftime("%Y-%m-%d-%H-%M-%S")
 
        # onglet prend la valeur d'index 0 du tuple (le nom des tables)
        onglet = table[0]
        # on ajoute à la feuille excel la valeur de "onglet", 1ere itération
        # onglet : connaissances
        sheet.append(onglet)

        # on récupére toutes les données de "onglet"
        requete_SQL = "SELECT * FROM " +str(onglet)
        print(table,"**")
        table_tb = pd.read_sql(requete_SQL, con)
        print(table,"--")
        #on ajoute à la liste tb[] 
        tb.append(table_tb)
        nom_fichier = "BDD"+ str_now +".xlsx"

    with pd.ExcelWriter(nom_fichier) as writer:
        for i in range (0,len(sheet)) :
            tb[i].to_excel(writer, sheet_name=sheet[i], index=False )
        print(table_tb.head())
        print("C'est sauvegardé à "+str_now+" dans "+nom_fichier) 

    metadata("test.txt", "Enregistrement de la base dans le fichier", nom_fichier)
    con.close() 
 
    
def rechargement(nom_base, fichier):
        # connexion à la bdd
        engine = create_engine('postgresql://postgres:digifab@127.0.0.1:5432/postgres')
        con = engine.connect()
        xl = pd.ExcelFile(fichier)
        metadata("test.txt", "debut du rechargement", "")
        # pour tous les noms de tables récupérés par xl.sheet_names
        for nom_table, i in zip(xl.sheet_names, range(len(xl.sheet_names))):
            # data frame du fichier excel
            df = pd.read_excel(fichier, sheet_name = i, header=0, 
                               index_col=0, keep_default_na=True)
            # on récupère les données de la df pour transfert en sql
            df.to_sql(nom_table, con, if_exists = 'replace')
            metadata("test.txt", "CREATE TABLE", nom_table)
        # fermeture de la connexion
        con.close()    
  
           
def metadata(adresse, action, table):
    fichier = open(adresse, "a")
    temps = datetime.datetime.now()
    temps = temps.strftime("%Y-%m-%d %H:%M:%S")
    fichier.write(action+' '+table+' '+temps+'\n')
    fichier.close()
    

def test_metadonnees():
    sauvegarde_base_de_donnees("postgres")
    engine = create_engine('postgresql://postgres:digifab@127.0.0.1:5432/postgres')
    con = engine.connect()
    con.execute("""DROP TABLE types_bien""")
    con.close()
    rechargement("", "BDD2020-09-04-10-00-22.xlsx")

    
if __name__ == '__main__':
    test_robot_sauvegarde = True
    if test_robot_sauvegarde == True:      
        debut = datetime.datetime.now()        
        s = sched.scheduler()
        while datetime.datetime.now() < debut + timedelta(seconds=5):
            s.enter(2, 1, sauvegarde_base_de_donnees)
            s.run()