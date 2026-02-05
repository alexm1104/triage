import streamlit as st

st.set_page_config(page_title="Triage Clinique IPS Santé Plus", layout="wide")

st.title("🏥 Assistant Triage - Clinique IPS Santé Plus")

# --- ÉTAPE 1 : IDENTIFICATION & DIVULGATION (Stricte) ---
st.subheader("1️⃣ Accueil et Informations Légales")
col_adm1, col_adm2 = st.columns(2)

with col_adm1:
    dossier = st.radio("Avez-vous un dossier à la clinique ?", ["Oui", "Non"], horizontal=True)
    privé = st.toggle("Le patient sait que c'est une CLINIQUE PRIVÉE (frais à sa charge) ?")
    pas_medecin = st.toggle("Le patient sait qu'il n'y a PAS DE MÉDECIN (IPS/Inf uniquement) ?")

with col_adm2:
    lieu = st.selectbox("Point de service :", ["-- Choisir --", "Jonquière", "Saint-Félicien"])

# --- DÉLOCAGE DU TRIAGE ---
if privé and pas_medecin and lieu != "-- Choisir --":
    st.divider()
    st.subheader("2️⃣ Analyse du besoin (Recherche par mot-clé)")
    recherche = st.text_input("Quels sont vos symptômes ?").lower()

    if recherche:
        t = {"prof": "IPS", "temps": "30 min", "prix": 0.0, "depot": 0.0, "annul": "48h", "notes": []}
        frais_ouv = 35.0 if dossier == "Non" else 0.0
        
        # --- MODULE SANTÉ MENTALE (SM) ---
        sm_keywords = ["mentale", "anxiété", "dépression", "sommeil", "alimentaire", "burnout", "deuil", "séparation", "épuisement", "tda", "tdah"]
        
        if any(x in recherche for x in sm_keywords):
            # 1. Sécurité et Âge
            st.error("🚨 SÉCURITÉ : Avez-vous des intentions de faire du mal à vous ou à autrui ?")
            if st.radio("Réponse sécurité :", ["Non", "Oui"]) == "Oui":
                st.critical("URGENCE : Composez le 911 ou allez à l'hôpital.")
            elif st.number_input("Âge :", 0, 115, 18) < 18:
                st.warning("Désolé, nous ne voyons que les adultes (18+) en santé mentale.")
            else:
                # 2. Les 11 points de l'IPSSM (Point 3.a.iv)
                with st.expander("📝 Informations sur la consultation IPSSM (Points 1 à 11)", expanded=True):
                    st.write("""
                    1. Téléconsultation avec l’IPSSM d’une durée de 50 min.
                    2. Approche personnalisée selon votre condition.
                    3. Validation des antécédents personnels et familiaux.
                    4. Demande les investigations nécessaires (tests, etc.).
                    5. Pose les diagnostics.
                    6. Prescrit et ajuste la médication au besoin.
                    7. Donne des arrêts de travail si nécessaire.
                    8. Coût de 250$ pour la première consultation (Générale).
                    9. Si nécessaire, les suivis sont de 20 min à 195$.
                    10. Un dépôt de 100$ est demandé avant la prise de rendez-vous.
                    11. Lien de connexion Telus Santé envoyé par courriel.
                    """)

                # 3. Logique TDA / TDAH vs Générale
                if "tda" in recherche or "tdah" in recherche:
                    st.success("✅ Trajectoire TDA/TDAH (2 Consultations)")
                    t.update({
                        "prof": "Infirmière (1h) ET IPSSM (50min)",
                        "temps": "1h + 50min (2 RDV)",
                        "prix": 195.0, # Prix de la première rencontre infirmière
                        "depot": 100.0,
                        "annul": "72h",
                        "note": "Note : La consultation IPSSM suivra celle de l'infirmière. Un dépôt de 100$ est requis pour l'IPSSM."
                    })
                else:
                    st.success("✅ Trajectoire Santé Mentale Générale")
                    t.update({
                        "prof": "IPSSM (Télémédecine)",
                        "temps": "50 min",
                        "prix": 250.0,
                        "depot": 100.0,
                        "annul": "72h"
                    })

        # --- SCRIPT FINAL ---
        if t["prix"] > 0:
            st.divider()
            st.subheader("💬 Script Final à lire au patient")
            
            total_initial = t["prix"] + frais_ouv
            
            script = f"""
            > "J'ai bien noté. Votre rendez-vous se déroulera en **{t['temps']}**. 
            > Notez que nous ne traiterons que le problème mentionné; tout ajout supplémentaire peut entraîner des frais.
            > 
            > **Frais et Annulation :**
            > * Le coût de la première consultation est de **{total_initial:.2f} $** (incluant le 35$ d'ouverture de dossier).
            > * Un dépôt de **{t['depot']:.2f} $** est requis pour confirmer le rendez-vous avec l'IPSSM.
            > * Notre politique d'annulation est de **{t['annul']}**. En cas d'absence ou d'annulation tardive, **50% des frais** seront chargés à votre dossier.
            > 
            > **Ponctualité :**
            > * Veuillez vous connecter (ou vous présenter) **5 à 10 minutes à l'avance**. 
            > * Un retard de **10 minutes** est considéré comme une absence."
            """
            st.markdown(script)

else:
    st.info("Veuillez valider les informations d'identification et les divulgations obligatoires pour débuter.")
