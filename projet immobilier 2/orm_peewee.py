"""
Created on Wed Jul  8 00:22:51 2020

@author: Sabrina
"""


from peewee import Model
from peewee import (AutoField, DateField, TextField, IntegerField,
                    CharField, ForeignKeyField)
from playhouse.postgres_ext import (PostgresqlExtDatabase, ArrayField, 
                                    FloatField)
from flask_login import UserMixin

# un fichier contient les instructions de connexion a la base de donnée
# fichier = open("/Users/alexis/Desktop/stageprojetimmobilier/Projet immobilier"+
#                "/test_fichier.rtf", "r")

# lignes = fichier.readlines()
# liste = []

# for ligne in lignes:
#     if ligne != '\\\n':
#         lignepropre = ligne.replace("\\", "")
#         lignepropre = lignepropre.replace("\n", "")
#         lignepropre = lignepropre.replace("}", "")
#         liste += [lignepropre]

#aprés lecture de ce fichier une connexion est initialisé
# db = PostgresqlExtDatabase(host='ec2-52-48-65-240.eu-west-1.compute.amazonaws.com',
#                             database='d1nt81188b39lc',
#                             user='lrkqkvxihsqpig',
#                             password='e80664f7359aca14babdcc81dea263fa530f64321d7ce25e713214f786e9f193',
#                             port=5432)

db = PostgresqlExtDatabase(host='localhost',
                            database='immo',
                            user='postgres',
                            password='0904',
                            port=5432)

class BaseModel(Model):
      
    class Meta :
        database = db

class Logement(BaseModel):
    
    id_logement = AutoField()
    id_type = IntegerField()
    surface = IntegerField()
    nb_chambre = IntegerField()
    prix = FloatField()
    prix_metre_carre = IntegerField()
    id_ville = IntegerField()
    cp = TextField()
    quartier = TextField()
    dpe = TextField()
    energie = TextField()
    annee = TextField()
    taxe_fonciere = TextField()
    description = TextField()
    contact = TextField()
    date_publi = DateField()
    lien = TextField(unique = True)
    date_crea = DateField()
    image = TextField(null = True)
    

class Ville(BaseModel):
    
    id_ville = AutoField()
    nom = TextField(unique = True)
    prix_moyen_maison = FloatField(null = True)
    prix_moyen_appart = FloatField(null = True)
    loyer_moyen_maison = FloatField(null = True)
    loyer_moyen_appart = FloatField(null = True)

class Proximite(BaseModel):
    id_proximite = AutoField()
    id_ville = IntegerField(unique = True)
    nombre_ecole = TextField()
    nombre_habitant = TextField()
    moins_25ans = TextField()
    nombre_commerce = TextField()
    
    
class Types_bien(BaseModel) : 
   
    id_type = AutoField()
    type_bien = TextField()
    
class Cave(BaseModel):
    id_cave = AutoField()
    id_logement = IntegerField()
    
class Jardin(BaseModel):
    id_jardin = AutoField()
    id_logement = IntegerField()
    surface_t = TextField()
    
class Exterieur(BaseModel):
    #balcon ou terrasse
    id_ext = AutoField()
    id_logement = IntegerField()
    
class Stationnement(BaseModel):
    id_station = AutoField()
    id_logement = IntegerField()
    
class Utilisateurs(BaseModel, UserMixin):
    """Ceci est la modélisation d'un utilisateur au sein du code, il
    possède un ID unique autoincrémenté côté base de donnée, des
    caractéristiques : un mail et un pseudo """
    # Identifiant
    id_utilisateur = AutoField()
    mail = TextField(unique=True)
    pseudo = TextField(unique=True)
    niveau = IntegerField(default=0)


    def __repr__(self):
                return "%d/%s/%s" % (self.id_utilisateur, self.pseudo, self.mail)
            
      

class Mot_de_passe(BaseModel):
    id_utilisateur = IntegerField()
    mot_de_passe = TextField()

class Coordonnees(BaseModel):
    id_ville = IntegerField()
    x = FloatField()
    y = FloatField()

def chargement_utilisateur(pseudo=None, id_utilisateur=None):
    """Retourne un utilisateur par son pseudo ou son id, retourne None si
    le chargement a échoué."""
    if pseudo:
        for utilisateur in (Utilisateurs.select()
                                       .where(Utilisateurs.pseudo == pseudo)):
            return utilisateur
    
    if id_utilisateur:
        for utilisateur in (Utilisateurs.select()
                                       .where(Utilisateurs.id_utilisateur ==
                                              id_utilisateur)):
            return utilisateur

    return None

def cre_proxi(villes):
    for ville in villes:
        Proximite.create(id_ville=ville.id_ville,nombre_ecole='nombre inconnue',
                         nombre_habitant='nombre inconnue',moins_25ans='nombre inconnue',
                         nombre_commerce='nombre inconnue')
        
if __name__ == '__main__':
    crea_table = False
    test_utilisateur = False
    
    if crea_table:
        tout = (Logement, Ville, Types_bien, Utilisateurs, 
                        Mot_de_passe, Proximite)   
        #création d'une table
        db.drop_tables([Logement, Ville, Types_bien, Utilisateurs,Mot_de_passe,
                        Proximite,Cave,Jardin,Exterieur,Stationnement,Coordonnees])
        db.create_tables([Logement, Ville, Types_bien, Utilisateurs,Mot_de_passe,
                          Proximite,Cave,Jardin,Exterieur,Stationnement,Coordonnees])     
   
   
    if test_utilisateur:  
        for utilisateur in (Utilisateurs.select()
                                       .where(Utilisateurs.pseudo == "Sarah")):
            Sarah = utilisateur
        Sarah._test_SUCCESS()
        
     





