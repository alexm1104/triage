import streamlit as st

st.set_page_config(page_title="Triage IPS Santé Plus", page_icon="🏥", layout="wide")

st.title("🏥 Assistant Triage & Facturation - IPS Santé Plus")
st.caption("Version 2.0 : Gestion fiscale et protocoles cliniques")

# --- PARAMÈTRES PATIENT ---
with st.sidebar:
    st.header("👤 Dossier Patient")
    point_service = st.radio("Point de service", ["Jonquière", "Saint-Félicien"])
    age = st.number_input("Âge du patient", min_value=0, max_value=115, value=18)
    nouveau = st.toggle("Nouveau patient (Frais 35$)")
    st.divider()
    st.write("Exonération de taxes active (sauf SAAQ)")

# --- RECHERCHE PAR SYMPTÔMES ---
st.subheader("🕵️ Symptôme ou Motif")
recherche = st.selectbox("Sélectionnez le besoin :", [
    "-- Choisir --",
    "Toux / Rhume / Congestion",
    "Mal de gorge / Difficulté à avaler",
    "Douleur à l'oreille / Oreille bouchée",
    "Brûlure urinaire / Envie fréquente (Femme)",
    "Brûlure urinaire / Douleur (Homme)",
    "Dépistage ITSS (Sans symptômes)",
    "Plaies / Écoulements génitaux (Symptômes ITSS)",
    "Santé Mentale (Anxiété, Sommeil, TDAH)",
    "Lavage d'oreilles",
    "Examen SAAQ (Formulaire conducteur)",
    "Bilan de Santé complet"
])

# --- VARIABLES DE CALCUL ---
if recherche != "-- Choisir --":
    trajectoire = {"prof": "", "temps": "", "prix": 0.0, "taxable": False, "note": ""}
    
    # FILTRE ROUGE (Toujours présent)
    st.error("⚠️ **SÉCURITÉ :** Le patient a-t-il une difficulté respiratoire sévère ou une douleur thoracique ?")
    alerte_vitale = st.checkbox("OUI - Signes de gravité")

    if alerte_vitale:
        st.critical("🚨 **NE PAS RÉSERVER.** Diriger vers le 911 ou l'Urgence.")
    else:
        # LOGIQUE DE TRIAGE
        if "SAAQ" in recherche:
            st.warning("📋 **CONDITION SAAQ :** Le patient a-t-il eu une visite médicale à la clinique dans les 2 dernières années ?")
            visite_recente = st.radio("Visite < 2 ans ?", ["Non / Inconnu", "Oui"])
            
            if visite_recente == "Oui":
                trajectoire.update({"prof": "IPS", "temps": "30 min", "prix": 160.0, "taxable": True})
            else:
                st.error("❌ **IMPORTANT :** On ne peut pas remplir le formulaire si aucune visite médicale n'a eu lieu depuis 2 ans. Prévoir un Bilan de Santé avant l'examen SAAQ.")

        elif "Toux" in recherche:
            trajectoire.update({"prof": "IPS ou Infirmière", "temps": "20-30 min", "prix": 138.0})

        elif "Femme" in recherche:
            trajectoire.update({"prof": "Infirmière (OC)", "temps": "20 min", "prix": 95.0})

        elif "Lavage" in recherche:
            trajectoire.update({"prof": "Infirmière", "temps": "30 min", "prix": 40.0})

        elif "Bilan" in recherche:
            trajectoire.update({"prof": "IPS", "temps": "45-60 min", "prix": 350.0})

        # --- AFFICHAGE ET CALCUL ---
        if trajectoire["prix"] > 0:
            st.divider()
            col1, col2 = st.columns(2)
            
            with col1:
                st.success(f"### Trajectoire : {trajectoire['prof']}")
                st.write(f"⏱️ **Durée :** {trajectoire['temps']}")
                st.write(f"📍 **Lieu :** {point_service}")

            with col2:
                # CALCUL FINANCIER
                base = trajectoire["prix"]
                ouverture = 35.0 if nouveau else 0.0
                sous_total = base + ouverture
                
                if trajectoire["taxable"]:
                    taxe = sous_total * 0.14975
                    total = sous_total + taxe
                    label_taxe = f"Taxes (TPS/TVQ) : {taxe:.2f} $"
                else:
                    taxe = 0.0
                    total = sous_total
                    label_taxe = "Services médicaux exonérés de taxes"

                st.subheader(f"Total : {total:.2f} $")
                st.caption(f"Consultation : {base:.2f} $")
                if nouveau: st.caption(f"Ouverture de dossier : 35.00 $")
                st.write(f"🧾 {label_taxe}")
