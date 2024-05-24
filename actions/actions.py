from typing import Any, Text, Dict, List
import random
import string
import sqlite3
from datetime import datetime, timedelta

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import Restarted

def add_resa(nom, numero,date,tel,nb_personne):
    with sqlite3.connect('sqlite.db') as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO reservations (nom,numero,date,tel,nb_personne) VALUES(?,?,?,?,?)", (nom,numero,date,tel,nb_personne))
        return cursor.fetchone()

def check_resa(num_resa):
    with sqlite3.connect('sqlite.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM reservations WHERE numero = ?", (str(num_resa),))
        rows = cursor.fetchone()
        return rows

def delete_resa(num_resa):
    with sqlite3.connect('sqlite.db') as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM reservations WHERE numero = ?", (str(num_resa),))
        return True


def get_tomorrow_date_string():
    # Obtenir la date actuelle
    today = datetime.now()
    # Calculer la date de demain
    tomorrow = today + timedelta(days=1)
    # Formater la date de demain au format dd/mm/yyyy
    tomorrow_string = tomorrow.strftime("%Y-%m-%d")
    return tomorrow_string

def get_today_date_string():
    # Obtenir la date actuelle
    today = datetime.now()
    # Formater la date de demain au format dd/mm/yyyy
    today_string = today.strftime("%Y-%m-%d")
    return today_string

def generate_random_string(length=10):
    # Combine letters (both uppercase and lowercase) and digits
    characters = string.ascii_letters + string.digits
    # Generate a random string of the specified length
    random_string = ''.join(random.choice(characters) for i in range(length))
    return random_string

class ActionSubmitHotelBooking(Action):

    def name(self) -> Text:
        return "action_submit_hotel_booking"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print('TEST')
        city = tracker.get_slot("city")
        date = tracker.get_slot("date")
        print(city)
        print(date)
        if city and date:
            dispatcher.utter_message(
                template="utter_confirm_booking",
                city=city,
                date=date
            )
        else:
            dispatcher.utter_message(template="utter_default")
        
        return []


class ActionVerifDateAndPersonne(Action):

    def name(self) -> Text:
        return "action_verif_date_and_personnes"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        nbPersonnes = tracker.get_slot("nb_personne")
        date = tracker.get_slot("date")
        if nbPersonnes and date:
            dispatcher.utter_message(
                template="utter_test",
                nbPersonnes=nbPersonnes,
                date=date
            )
        else:
            dispatcher.utter_message(template="utter_default")

        return []

class ActionCheckDispoDateAndPersonne(Action):

    def name(self) -> Text:
        return "action_check_if_date_and_personnes_dispo"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        nbPersonnes = tracker.get_slot("nb_personne")
        date = tracker.get_slot("date")
        if nbPersonnes and date:
            dispatcher.utter_message(
                template="utter_resa_est_dispo",
                nbPersonnes=nbPersonnes,
                date=date
            )
        else:
            dispatcher.utter_message(template="utter_default")

        return []
class ActionConfirmResa(Action):

    def name(self) -> Text:
        return "action_confirm_resa"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        nbPersonnes = tracker.get_slot("nb_personne")
        date = tracker.get_slot("date")
        nom = tracker.get_slot("nom")
        tel = tracker.get_slot("tel")
        resa = generate_random_string()
        if nbPersonnes and date and nom and tel and resa:
            project_id = add_resa(nom, resa, date, tel, nbPersonnes)

            dispatcher.utter_message(
                template="utter_confirm_resa",
                nbPersonnes=nbPersonnes,
                date=date,
                tel=tel,
                nom=nom,
                resa=resa
            )
        else:
            dispatcher.utter_message(template="utter_default")

        return []

class ActionCheckNumeroResa(Action):

    def name(self) -> Text:
        return "action_check_numero_resa"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        resa = tracker.get_slot("numero_resa")
        rows = check_resa(resa)
        print(rows)
        if rows is not None and len(rows) > 0:

            print(rows[3])

            dispatcher.utter_message(
                template="utter_resa_numero_is_valid",
                numero_resa=resa,
                check_nom_resa=rows[1],
                check_date_resa=rows[3],
                check_tel_resa=rows[4],
                check_nb_personne_resa=rows[5],
            )
        else:
            dispatcher.utter_message(template="utter_resa_numero_is_wrong")

        return []

class ActionAnnulationResa(Action):

    def name(self) -> Text:
        return "action_annulation_resa"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        resa = tracker.get_slot("numero_resa")
        is_deleted = delete_resa(resa)

        # Return Restarted event to clear the conversation state
        if is_deleted:



            dispatcher.utter_message(
                template="utter_resa_est_annulee",
                numero_resa=resa,
            )
        else:
            dispatcher.utter_message(template="utter_resa_numero_is_wrong")

        return []
