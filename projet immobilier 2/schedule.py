from scrap_bdd import recuperation_superimmo, insert_bien, liens_super
from prix_moyen import recuperation_prix2
from apscheduler.schedulers.background import BackgroundScheduler
from orm_peewee import db, Logement, Types_bien, Ville
import datetime
import pandas as pd
from vérification import verification

def sensor():   
    
    print("lancement schedule")
    dico_super = [
        {"lien":"https://www.superimmo.com/achat/immeuble/haute-normandie,basse-normandie/a"+
          "-renover","nombre":1},
        {"lien":"https://www.superimmo.com/achat/haute-normandie"+
          ",basse-normandie/a-renover","nombre":1}]  
    madate = datetime.datetime.now()  
    
    if madate.hour == 11:
        donnée_ville = Ville.select()
        donnée_logement = Logement.select()
        donnée_types_bien = Types_bien.select()
        
        df_ville = pd.DataFrame(list(donnée_ville.dicts()))
        df_ville.to_excel("ville.xlsx")
        
        df_logement = pd.DataFrame(list(donnée_logement.dicts()))
        df_logement.to_excel("logement.xlsx")
        
        df_types_bien = pd.DataFrame(list(donnée_types_bien.dicts()))
        df_types_bien.to_excel("type_bien.xlsx")
        
        liens_recherche = liens_super(dico_super)
        liste_dico = recuperation_superimmo(liens_recherche)    
        nouvelles_villes = insert_bien(liste_dico)        
        try :            
            recuperation_prix2(nouvelles_villes)
        except :
            pass
        else:
            verification()
        return     
                    
      
if __name__ == '__main__':
    lancement = True
    if lancement == True:                    
        sched = BackgroundScheduler(daemon=True)
        sched.add_job(sensor, 'interval', hours=1)
        sched.start()