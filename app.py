import streamlit as st

# Configuration de l'application
st.set_page_config(page_title="Triage IPS Santé Plus", page_icon="🏥", layout="wide")

st.title("🏥 Système Expert de Triage - Clinique IPS Santé Plus")
st.caption("Protocoles INESSS, Ordonnances Collectives et Gestion Fiscale Intégrés")

# --- BARRE LATÉRALE : DONNÉES PATIENT ---
with st.sidebar:
    st.header("👤 Dossier Patient")
    age = st.number_input("Âge du patient", min_value=0, max_value=115, value=18)
    nouveau = st.toggle("Nouveau patient (Frais d'ouverture 35$)")
    st.divider()
    st.info("Note : Les services médicaux sont exonérés de taxes. Seuls les formulaires administratifs (SAAQ) sont taxables.")

# --- MODULE DE RECHERCHE PAR SYMPTÔMES ---
st.subheader("🔍 Quelle est la raison de consultation ?")
recherche = st.selectbox("Sélectionnez le symptôme ou le motif :", [
    "-- Choisir un motif --",
    "Toux / Fièvre / Suspicion Pneumonie ou MPOC",
    "Mal de gorge / Difficulté à avaler (Pharyngite)",
    "Douleur à l'oreille / Oreille bouchée (Otite)",
    "Brûlure urinaire / Envie fréquente (Infection urinaire)",
    "Pertes vaginales ou Écoulement urétral (ITSS)",
    "Dermato : Plaque rouge, chaude et enflée (Cellulite)",
    "Dermato : Éruption de bulles d'un seul côté (Zona)",
    "Dermato : Verrues ou Acrochordons (Cryothérapie)",
    "Piqûre de tique (Maladie de Lyme)",
    "Hypertension (Suivi ou lecture élevée)",
    "Santé Mentale (Anxiété, Sommeil, TDAH - Adulte)",
    "Examen SAAQ (Formulaire conducteur)",
    "Bilan de Santé Complet / Check-up"
])

if recherche != "-- Choisir un motif --":
    # Variables par défaut
    trajectoire = {"prof": "IPS", "temps": "30 min", "prix": 138.0, "taxable": False, "note": ""}
    er_redirect = False

    # 1. ÉVALUATION DES SIGNES DE GRAVITÉ (DROIT DE VETO)
    with st.expander("🚨 FILTRE DE SÉCURITÉ (À vérifier en premier)", expanded=True):
        st.write("Si le patient présente l'un de ces signes, ne pas prendre de rendez-vous.")
        c1, c2 = st.columns(2)
        with c1:
            s1 = st.checkbox("Difficulté respiratoire sévère (incapable de parler)")
            s2 = st.checkbox("Douleur subite et intense à la poitrine")
        with c2:
            s3 = st.checkbox("Confusion, léthargie ou perte de conscience")
            s4 = st.checkbox("Fièvre très élevée (>40°C) avec état général altéré")
    
    if s1 or s2 or s3 or s4:
        er_redirect = True

    # 2. LOGIQUE MÉDICALE DÉTAILLÉE
    else:
        # --- RESPIRATOIRE ---
        if "Toux" in recherche:
            if st.checkbox("Le patient est-il très essoufflé ou immunosupprimé ?"):
                trajectoire.update({"prof": "IPS (Prioritaire)", "temps": "45 min", "prix": 180.0})
            else:
                trajectoire.update({"prof": "Infirmière (OC-017)", "temps": "30 min", "prix": 95.0})

        # --- ORL ---
        elif "Gorge" in recherche:
            if st.checkbox("Incapable d'avaler sa salive ou d'ouvrir la bouche ?"):
                er_redirect = True
            else:
                trajectoire.update({"prof": "IPS ou Infirmière", "temps": "20 min", "prix": 95.0, "note": "Test rapide Strep inclus."})
        
        elif "Oreille" in recherche:
            trajectoire.update({"prof": "IPS ou Infirmière", "temps": "20 min", "prix": 138.0})

        # --- URINAIRE ---
        elif "urinaire" in recherche:
            sexe = st.radio("Sexe du patient :", ["Femme", "Homme"])
            if sexe == "Homme":
                trajectoire.update({"prof": "IPS (Toujours complexe chez l'homme)", "prix": 138.0})
            else:
                if st.checkbox("Fièvre, douleur au dos ou grossesse ?"):
                    trajectoire.update({"prof": "IPS (Prioritaire)", "prix": 138.0})
                else:
                    trajectoire.update({"prof": "Infirmière (OC)", "prix": 95.0})

        # --- DERMATO ---
        elif "Cellulite" in recherche:
            if st.checkbox("Fièvre, frissons ou rougeur qui s'étend rapidement ?"):
                er_redirect = True
            else:
                trajectoire.update({"prof": "IPS", "prix": 138.0})

        elif "Zona" in recherche:
            if st.checkbox("Bulles sur le visage ou près de l'œil ?"):
                er_redirect = True
                trajectoire["note"] = "Urgence ophtalmique potentielle."
            else:
                trajectoire.update({"prof": "IPS", "prix": 138.0})

        elif "Verrues" in recherche:
            trajectoire.update({"prof": "Infirmière", "prix": 50.0, "note": "Acte de cryothérapie."})

        # --- LYME ---
        elif "Lyme" in recherche:
            tique = st.checkbox("Tique attachée > 36h et retrait < 72h ?")
            if age >= 8 and tique:
                trajectoire.update({"prof": "Infirmière (OC)", "prix": 95.0})
            else:
                trajectoire.update({"prof": "IPS", "prix": 138.0})

        # --- ADMINISTRATIF & SAAQ ---
        elif "SAAQ" in recherche:
            visite = st.radio("Visite médicale à la clinique dans les 2 dernières années ?", ["Non", "Oui"])
            if visite == "Oui":
                trajectoire.update({"prof": "IPS", "prix": 160.0, "taxable": True})
            else:
                st.error("❌ Action : Le patient doit d'abord passer
