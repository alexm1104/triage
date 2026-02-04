import streamlit as st

# 1. TOUJOURS COMMENCER PAR L'IMPORTATION
st.set_page_config(page_title="Triage IPS Santé Plus", layout="wide")

st.title("🏥 Assistant Triage - Clinique IPS Santé Plus")

# --- ÉTAPE 1 : IDENTIFICATION (Obligatoire) ---
st.subheader("1️⃣ Identification de l'appel")
col_id1, col_id2 = st.columns(2)

with col_id1:
    point_service = st.selectbox("Clinique visée :", ["-- Choisir --", "Jonquière", "Saint-Félicien"])
with col_id2:
    deja_dossier = st.selectbox("Le client a-t-il déjà un dossier ?", ["-- Choisir --", "Oui", "Non"])

# On ne montre la suite que si l'étape 1 est complétée
if point_service != "-- Choisir --" and deja_dossier != "-- Choisir --":
    st.divider()
    
    # --- ÉTAPE 2 : RECHERCHE PAR SYMPTÔME ---
    st.subheader("2️⃣ Recherche clinique")
    recherche = st.text_input("Tapez le symptôme mentionné par le patient (ex: oreille, gorge, urine) :").lower()

    if recherche:
        trajectoire = {"prof": "À déterminer", "prix": 0.0, "note": ""}
        frais_ouverture = 35.0 if deja_dossier == "Non" else 0.0

        # --- MODULE SPÉCIFIQUE : OREILLE (OC-006 / OC-014) ---
        if "oreille" in recherche or "otite" in recherche:
            st.info("👂 **Analyse Otite détectée**")
            
            st.markdown("**Questions à poser au patient :**")
            c1, c2 = st.columns(2)
            with c1:
                q1 = st.checkbox("Le patient a-t-il des vertiges ou des pertes d'équilibre ?")
                q2 = st.checkbox("Y a-t-il un écoulement de pus ou de sang important ?")
            with c2:
                q3 = st.checkbox("La douleur est-elle apparue suite à un choc ou un objet inséré ?")
                q4 = st.toggle("La douleur augmente-t-elle si on touche/tire l'oreille ?")

            # Logique d'aiguillage
            if q1 or q2 or q3:
                trajectoire.update({"prof": "IPS (Exclusion OC)", "prix": 180.0, "note": "Cas complexe : Possible perforation ou atteinte interne."})
            elif q4:
                trajectoire.update({"prof": "Infirmière (OC-014 - Otite Externe)", "prix": 140.0, "note": "Appliquer le protocole d'otite externe."})
            else:
                trajectoire.update({"prof": "Infirmière (OC-006 - Otite Moyenne)", "prix": 140.0, "note": "Appliquer le protocole d'otite moyenne aiguë."})

        # --- AFFICHAGE DU RÉSULTAT ---
        if trajectoire["prix"] > 0:
            st.divider()
            st.success(f"✅ **Résultat : Orientez vers {trajectoire['prof']}**")
            
            total = trajectoire["prix"] + frais_ouverture
            
            st.markdown(f"""
            ### 💬 Script pour la secrétaire :
            > "Je vous ai réservé un rendez-vous à notre clinique de **{point_service}**. 
            > Vous serez vu par notre **{trajectoire['prof']}**. 
            > Le montant total à prévoir est de **{total:.2f} $**. 
            > *Note : {trajectoire['note']}*"
            """)
