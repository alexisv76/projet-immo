#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 16 16:03:20 2020

@author: Sabrina
"""
from orm_peewee import Ville, Logement, db, Types_bien,Cave,Coordonnees
from matplotlib import pyplot as plt
import random
import pandas as pd
import seaborn as sns



def obtention_id():
    
    id_appartement = Types_bien.select().where(Types_bien.type_bien
                                               == "appartement")[0].id_type
    id_maison = Types_bien.select().where(Types_bien.type_bien
                                          == "maison")[0].id_type
    id_immeuble = Types_bien.select().where(Types_bien.type_bien
                                            == "immeuble")[0].id_type
    return id_appartement, id_maison, id_immeuble


def selection_lien(ville): 
    
    top = []
    appartement = []
    maison = []
    immeuble = []
    id_appartement, id_maison, id_immeuble = obtention_id()
    
    ville_choisie = Ville.select().where(Ville.nom == ville)
    id_ville = ville_choisie[0].id_ville
    prix_appartement = ville_choisie[0].prix_moyen_appart
    prix_maison = ville_choisie[0].prix_moyen_maison
    
    annonces = Logement.select(Logement, Types_bien).join(
            Types_bien, on=(Logement.id_type == Types_bien.id_type)).where(
            Logement.id_ville == id_ville)
    
    for annonce in annonces:
        id_type = annonce.id_type
        if id_type == id_appartement:
            try:
                if annonce.prix_metre_carre < prix_appartement:
                    top += [annonce]
                else:
                    appartement += [annonce]
            except:
                appartement += [annonce]
        
        if id_type == id_maison:
             try:
                 if annonce.prix_metre_carre < prix_maison:
                     top += [annonce]
                 else:
                     maison += [annonce]  
             except:
                 maison += [annonce]
                 pass
        if id_type == id_immeuble:
            immeuble += [annonce]
    return top, appartement, maison, immeuble, prix_appartement, prix_maison


def top_annonces_f():
    top_annonces = []
    id_appartement, id_maison, id_immeuble = obtention_id()
    join = Logement.select(Logement, Ville).join(
            Ville, on=(Logement.id_ville == Ville.id_ville))
    
    for j in join:
        try:
            if j.id_type == id_appartement:
                if j.prix_metre_carre < j.ville.prix_moyen_appart:
                    top_annonces += [j]
            if j.id_type == id_maison:
                if j.prix_metre_carre < j.ville.prix_moyen_maison:
                    top_annonces += [j] 
        except:
            pass
    return top_annonces


# def recherche_personnalisee(liste):
    
#     conditions = ((liste[0]))    
#     if len(liste) > 1:
#         for element in liste[1:]:
#             conditions &= (element)
#     annonces_perso = Logement.select(
#         Logement, Types_bien).join(Types_bien, on=(
#             Logement.id_type == Types_bien.id_type)).where(conditions)            
    # return annonces_perso

def recherche_personnalisee(nb_join,jointures,liste):
    
    conditions = ((liste[0]))    
    if len(liste) > 1:
        for element in liste[1:]:
            conditions &= (element)
            
    if nb_join == 0:
        annonces_perso = Logement.select(
        Logement, Types_bien)
        
    if nb_join == 1:
        annonces_perso = Logement.select(
        Logement, Types_bien,jointures[0])
        
    if nb_join == 2:
        annonces_perso = Logement.select(
        Logement, Types_bien,jointures[0],jointures[1])
        
    if nb_join == 3:
        annonces_perso = Logement.select(
        Logement, Types_bien,jointures[0],jointures[1],jointures[2])
        
    if nb_join == 4:
        annonces_perso = Logement.select(
        Logement, Types_bien,jointures[0],jointures[1],jointures[2],jointures[3])
    
    annonces_perso = annonces_perso.join(Types_bien, on=(
            Logement.id_type == Types_bien.id_type))
    
    if nb_join >0:
        
        for join in jointures :
            annonces_perso = annonces_perso.join(join, on=(Logement.id_logement
                                                           == join.id_logement))
        
    annonces_perso  = annonces_perso.where(conditions)
    return annonces_perso
        
    
    
        
    
    

def graphique_index():
    
    #récuperation de des nos logements jointes à la table ville
    join = Logement.select(
        Logement, Ville).join(Ville, on=(Logement.id_ville == Ville.id_ville))
     
    #transformation de la query peewee en dataframe          
    df = pd.DataFrame(list(join.dicts()))
    nbr = df[['nom', 'prix']].groupby('nom').count().sort_values(by='prix', 
                                                                 ascending=False)
    nbr.reset_index(0, inplace=True)
    nbr.rename(columns={'prix':'Nb_annonces'}, inplace=True)
    nbr.head()
    nbr = nbr.loc[:20]
    
    plt.figure(figsize=(10, 6))
    sns.barplot(x=nbr['nom'], y=nbr['Nb_annonces'], palette="Reds_r")
    plt.xlabel('\nville', fontsize=15, color='#c0392b')
    plt.ylabel("Nombre d'annonces\n", fontsize=15, color='#c0392b')
    plt.title("Nombre d'annonces par ville", fontsize=18, color='#e74c3c')
    plt.xticks(rotation=75)
    plt.tight_layout()
    image = "static/img/graph_index.jpg"
    plt.savefig(image)
    return image
    
    
def graphique_annonce(ville):
     join = Logement.select(Logement,Ville, Types_bien).join(Ville, on=
                                        (Logement.id_ville == Ville.id_ville
                                         )).join(Types_bien, on=(
                                         Logement.id_type == Types_bien.id_type
                                         )).where(Ville.nom == ville) 
                                      
     df = pd.DataFrame(list(join.dicts()))
     plt.figure(figsize=(10, 6))
     sns.barplot(x=df['prix'], y=df['surface'],
                 hue=df["type_bien"], dodge=False)
     plt.xlabel('\nprix', fontsize=15, color='#c0392b')
     plt.ylabel("surface\n", fontsize=15, color='#c0392b')
     plt.title("prix et surfaces des annonces", fontsize=18, color='#e74c3c')
     plt.xticks(rotation=75)
     plt.tight_layout()
     image = "static/img/graph_recherche_perso"+ville+".jpg"
     image = image.replace(" ", "_")
     # plt.savefig(image)
     
     return image

