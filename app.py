import streamlit as st

st.set_page_config(page_title="Triage Clinique IPS Santé Plus", layout="wide")

st.title("🏥 Assistant Triage - Clinique IPS Santé Plus")

# --- ÉTAPE 1 : IDENTIFICATION & DIVULGATION ---
st.subheader("1️⃣ Accueil et Informations Légales")
col_adm1, col_adm2 = st.columns(2)

with col_adm1:
    dossier = st.radio("Avez-vous un dossier à la clinique ?", ["Oui", "Non"])
    privé = st.toggle("Le patient comprend que les examens sont à ses frais ?")
    pas_medecin = st.toggle("Le patient comprend qu'il n'y a PAS de médecin (IPS/Inf seulement) ?")

with col_adm2:
    lieu = st.selectbox("Clinique visée :", ["-- Choisir --", "Jonquière", "Saint-Félicien"])

# Bloquer la suite tant que l'accueil n'est pas validé
if privé and pas_medecin and lieu != "-- Choisir --":
    st.divider()
    
    # --- ÉTAPE 2 : RECHERCHE PAR MOTS-CLÉS ---
    st.subheader("2️⃣ Analyse du besoin")
    recherche = st.text_input("Quels sont vos symptômes ? (Boîte de recherche)").lower()

    if recherche:
        t = {"prof": "IPS", "temps": 0, "prix": 0.0, "depot": 0.0, "annul": "48h", "note": ""}
        frais_ouv = 35.0 if dossier == "Non" else 0.0

        # --- MODULE SANTÉ MENTALE ---
        if any(x in recherche for x in ["mentale", "anxiété", "dépression", "burnout", "sommeil", "tda"]):
            st.warning("🚨 **Sécurité :** Avez-vous des intentions de faire du mal à vous ou à autrui ?")
            danger = st.radio("Réponse :", ["Non", "Oui"])
            
            if danger == "Oui":
                st.error("🚨 ACTION : Composer le 911 ou présentez-vous à l'urgence.")
            else:
                age = st.number_input("Quel est votre âge ?", min_value=0, value=18)
                if age < 18:
                    st.error("❌ Désolé, nous ne traitons pas la clientèle de moins de 18 ans.")
                else:
                    if "tda" in recherche:
                        t.update({"prof": "Infirmière (1h) + IPSSM (50min)", "temps": 110, "prix": 195.0, "depot": 100.0, "annul": "72h"})
                        t["note"] = "Suivi par téléconsultation avec l'IPSSM."
                    else:
                        t.update({"prof": "IPSSM (Téléconsultation)", "temps": 50, "prix": 250.0, "depot": 100.0, "annul": "72h"})

        # --- AFFICHAGE DU SCRIPT FINAL ---
        if t["prix"] > 0:
            st.divider()
            st.subheader("💬 Script de fin d'appel")
            
            total_initial = t["prix"] + frais_ouv
            
            script = f"""
            > "La durée de votre rendez-vous sera de **{t['temps']} minutes**[cite: 37]. 
            > Notez que nous ne traiterons que le problème mentionné; tout ajout peut entraîner des frais[cite: 38].
            > 
            > **Frais et Annulation :**
            > * Le coût est de **{total_initial:.2f} $** (un dépôt de {t['depot']}$ est requis [cite: 23, 34]).
            > * Annulation : **{t['annul']}** d'avance, sinon 50% des frais seront chargés.
            > 
            > **Ponctualité :**
            > * Veuillez vous connecter **5 à 10 minutes à l'avance**[cite: 40].
            > * Un retard de **10 minutes** est considéré comme une absence[cite: 41].
            """
            st.markdown(script)
            if "IPSSM" in t["prof"]:
                st.info("📩 **Action :** Envoyer le questionnaire Telus Santé à remplir avant le rendez-vous[cite: 35, 42].")

else:
    st.info("Veuillez valider les informations d'accueil (Privé / Pas de médecin) pour continuer.")
