#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 16 11:41:15 2020

@author: Sabrina
"""

from flask_login import (LoginManager, UserMixin,
                                login_required, login_user, logout_user,
                                    current_user)
from flask import Flask, render_template, redirect, url_for, flash, session
from flask import request, Response
from orm_peewee import (db, Ville, Logement, Types_bien, Utilisateurs, 
                        chargement_utilisateur, Cave, Jardin, Exterieur,
                        Stationnement,Coordonnees,Proximite)
from lien_immo import (obtention_id, selection_lien, top_annonces_f,
                        recherche_personnalisee, graphique_index, graphique_annonce)
from playhouse.postgres_ext import (PostgresqlExtDatabase, ArrayField, 
                                    FloatField)
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
import folium
import math
import datetime
import orm_peewee
from orm_peewee import Utilisateurs,Mot_de_passe
from geopy.geocoders import Nominatim

app = Flask(__name__)

app.config.update(DEBUG=True,SECRET_KEY='secret_xxx')

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)


ville = "Le havre"
@app.route('/')
def accueil():
    villes = []
    villes_db = Ville.select().where(Ville.prix_moyen_maison.is_null(False))
    for ville in villes_db:
        villes += [ville.nom]
    image = graphique_index()    
    
    return render_template("index.html", villes=villes, image=image)


@app.route('/accueil2')
def accueil2():
    return render_template("indexinerte.html")


@app.route('/annonce', methods=["POST"])
def annonce():
    global ville
    ville = request.form["ville"]
    top, appartement, maison, immeuble, prix_appartement, prix_maison = selection_lien(ville)
    image = graphique_annonce(ville)
    
    if request.form["ville"] == "":
        ville = "Le havre"
    lenmaison = len(maison)
    lentop = len(top)
    lenimmeuble = len(immeuble)
    lenappart = len(appartement)
    return render_template("annonce.html",ville=ville, top=top, maison=maison
                           ,lenmaison=lenmaison, appartement=appartement,
                           immeuble=immeuble, lentop=lentop,
                           lenappart=lenappart, lenimmeuble=lenimmeuble,
                           prix_appartement=prix_appartement, prix_maison=
                           prix_maison, image=image)


@app.route('/critere')
def critere():
    types = ["appartement", "maison", "immeuble", "tout"]
    return render_template('critere.html',types=types)

@app.route('/recherche_perso', methods=['POST'])
def recherche_perso():
    num_page = request.form['num']
    nb_join = 0
    liste_join =[]
    cave = None
    jardin = None
    ext = None
    place = None
    
    if num_page != "":
        num_page = int(num_page)
        num_page += 1
    else : 
        num_page = 1
    try:
        num1 = request.form["num1"]
        num_page = int(num1)
    except:
        pass
    
    liste_recherche = []
    type_bien1 = request.form["types"]
    prix = request.form["prix"]
    prix2 = request.form["prix2"]
    metre = request.form["mettre"]
    metre2 = request.form["mettre2"]
    if type_bien1 == "":
        type_bien1 = ["maison"]
    if type_bien1 != "":
        if type_bien1 != "tout":
            liste_recherche = [Types_bien.type_bien==type_bien1]
        if type_bien1 == "tout":
            liste_recherche = [Logement.id_ville == Logement.id_ville]
        if prix != "":
            liste_recherche += [Logement.prix >= prix]
        if prix2 != "":
            liste_recherche += [Logement.prix <= prix2]
        if metre != "":
            liste_recherche += [Logement.surface >= metre] 
        if metre2 != "":
            liste_recherche += [Logement.surface <= metre2]
            
        if request.form.get('cave'):
            nb_join += 1
            liste_join += [Cave]
            cave = True
        
        if request.form.get('jardin'):
            nb_join += 1
            liste_join += [Jardin]
            jardin = True
        
        if request.form.get('ext'):
            nb_join += 1
            liste_join += [Exterieur]
            ext = True
        
        if request.form.get('place'):
            nb_join += 1
            liste_join += [Stationnement]
            place = True
            
    annonces = recherche_personnalisee(nb_join,liste_join,liste_recherche)
    
    
    page_max = math.ceil(len(annonces)/15)
    if num_page > page_max:
        num_page = 1
    premiere = 15 * (num_page-1)
    derniere = 15 * num_page
    annonces= annonces[premiere:derniere]
          
    return render_template("recherche_perso.html", type_bien1=type_bien1,
                           num_page=num_page, ville=ville, annonces=annonces,
                           premiere=premiere, derniere=derniere, prix=prix
                           ,prix2=prix2, metre=metre, metre2=metre2,
                           page_max=page_max,cave=cave,jardin=jardin,ext=ext,
                           place=place)
    
    
@app.route('/carte_interactive')
def carte():
    geolocator = Nominatim(user_agent = "x")
    lieu = geolocator.geocode(ville)
    coords = (lieu.latitude,lieu.longitude)
    if lieu == None:
        coords = (49.494,0.107)
    carte = folium.Map(location = coords, zoom_start=12)
    folium.Marker(coords,popup = ville).add_to(carte)
    html_map = carte._repr_html_()
    return render_template("carte_interactive.html",html_map = html_map)

@app.route('/carte')
def carte2():
    villes = Ville.select(Ville,Coordonnees,Proximite).join(Coordonnees, 
                                                            on=(Ville.id_ville 
                                                 == Coordonnees.id_ville))
    
    villes = villes.join(Proximite, on=(Ville.id_ville 
                                                 == Proximite.id_ville))
    villes = list(villes.dicts())
    return render_template('carte.html',villes=villes)
         
@app.errorhandler(405)
@app.errorhandler(404)
@app.errorhandler(500)
def page_not_found(e):

    return render_template("404.html")

@app.route('/creation_compte')
def creation_compte():
    """Envoie une template qui permet la creation d'un compte.
       les informations nécéssaires sont les suivante : un nom de compte
       une adresse mail, et le mot de passe désiré en double"""

    if 'nom_de_compte' in session :
        return redirect("/")
    return render_template("creation_compte.html")


@app.route('/traitement_creation_compte', methods=['POST'])
def traitement_creation_compte() :
    """Nous traiton le contenu du formulaire obtenu de la page de création
       Il est a noté que par sécurité le mot de passe de l'utilisateur ne doit
       JAMAIS être stocké sur la BDD en clair, et de limité au maximum les
       sotckage en variable en clair, si la requête est fait en HTTPS le mdp
       sera stocké au sein du formulaire encodé et donc ne sera jamais present
       sur le site sous quelque forme que ce soit en clair"""

    #Recuperation données formulaire
    nom_de_compte = request.form['nom_de_compte']
    mail = request.form['mail']

    #Verification que les mdp sont les même
    if request.form['mot_de_passe_1'] != request.form['mot_de_passe_2'] :
        return redirect("erreur_mdp")

    try :

        #Si non sallage du mot de passe avec werkzeug security
        mot_de_passe_sale = generate_password_hash(
                                            request.form['mot_de_passe_1'])

        today = datetime.datetime.today()

        utilisateur = orm_peewee.Utilisateurs.create(mail = mail,
                                        pseudo = nom_de_compte,
                                        date_crea = today)

        orm_peewee.Mot_de_passe.create(id_utilisateur = 
                                       utilisateur.id_utilisateur, mot_de_passe
                                       = mot_de_passe_sale)
        login_user(utilisateur)
        #Comunique a l'utilisateur le succès
        return redirect('/creation_success')
    except :

        #Si le compte existe deja redirige vers une page qui indique l'echec
        #de sa tentative de creation de compte
        return redirect('/creation_fail')


@app.route('/creation_fail')
def creation_fail() :
    return render_template('message_creation_fail.html')


@app.route('/creation_success')
def creation_success() :
    return render_template('message_creation_success.html')

@app.route('/message_connexion_success')
def message_connexion_success() :
    return render_template('message_connexion_success.html')

@app.route('/formulaire_authentification')
def authentification():
   
    "Le formulaire de connexion se contente de récupéré l'adresse et le mdp"
    return render_template("/formulaire_authentification.html")

@app.route('/traitement_authentification', methods=['GET','POST'])
def login():

    username = request.form['nom']
   
    
    utilisateur  = (Utilisateurs.select(Utilisateurs,Mot_de_passe)
         .join(Mot_de_passe, on=(Utilisateurs.id_utilisateur == 
                                  Mot_de_passe.id_utilisateur))
         .where(Utilisateurs.pseudo==username))
    if check_password_hash(utilisateur[0].mot_de_passe.mot_de_passe,
                                request.form['mot_de_passe']) :
    
        user = chargement_utilisateur(pseudo=username)
        
        login_user(user)
        return "connécté"
    else:
        return render_template('/formulaire_authentification.html')

@app.route('/test_connexion')
def test_connexion():
    print("-"*10)
    print(current_user)
    print(type(current_user))
    print(type(current_user.utilisateur))

    print("-"*10)
    return redirect("/")

@app.route('/connexion_success')
def connexion_success():
    # return render_template('message_connexion_success.html')
        return redirect('/accueil')

# *****************************


@app.route('/connexion_fail')
def connexion_fail() :
    return render_template('message_connexion_fail.html')


@app.route('/deconnexion')
def deconnexion():

    return render_template('page_deconnexion.html')


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return render_template('index.html')

@app.route("/admin")
def admin():
    villes = Ville.select()
    df = pd.DataFrame(list(villes.dicts()))
    tables = df.values.tolist()
    return render_template("admin.html",tables=tables)

@app.route('/jsondata', methods = ['POST'])
def worker():
    data = request.get_json(force=True)
    print(data)
    return "ok"


@login_manager.user_loader
def load_user(userid):
     utilisateur = chargement_utilisateur(id_utilisateur=userid)
     return utilisateur

if __name__ == '__main__':
    app.run(debug=True,use_reloader=False)