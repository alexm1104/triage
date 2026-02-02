import streamlit as st

st.set_page_config(page_title="Triage Clinique IPS Santé Plus", page_icon="🏥", layout="wide")

st.title("🏥 Assistant Triage Intelligent - IPS Santé Plus")
st.caption("Intégration des Protocoles Nationaux INESSS et Ordonnances Collectives")

# --- PARAMÈTRES PATIENT ---
with st.sidebar:
    st.header("👤 Dossier Patient")
    age = st.number_input("Âge du patient", min_value=0, max_value=115, value=18)
    nouveau = st.toggle("Nouveau patient (Frais 35$)")
    st.divider()
    st.write("Facturation exonérée (sauf SAAQ)")

# --- DICTIONNAIRE DE TRIAGE (Logique INESSS) ---
st.subheader("🕵️ Recherche par Symptômes")
motif = st.selectbox("Sélectionnez le motif principal :", [
    "-- Choisir --",
    "Toux / Suspicion Pneumonie ou MPOC",
    "Mal de gorge / Pharyngite",
    "Brûlure urinaire / Infection urinaire",
    "Écoulement urétral (Homme)",
    "Pertes vaginales inhabituelles",
    "Chlamydia / Gonorrhée (Dépistage ou partenaire)",
    "Maladie de Lyme (Piqûre de tique)",
    "Candidose buccale (Plaques blanches)",
    "Hypertension (HTA)",
    "Examen SAAQ",
    "Bilan de Santé"
])

if motif != "-- Choisir --":
    trajectoire = {"prof": "IPS", "temps": "30 min", "prix": 138.0, "taxable": False, "msg": ""}
    er_redirect = False

    # 1. FILTRE ROUGE UNIVERSEL (Signes de choc/détresse)
    with st.expander("🚨 Évaluation d'urgence (À vérifier systématiquement)", expanded=True):
        col_er1, col_er2 = st.columns(2)
        with col_er1:
            détresse = st.checkbox("Difficulté respiratoire sévère ou Stridor ?")
            confusion = st.checkbox("Confusion ou altération de l'état de conscience ?")
        with col_er2:
            douleur_c = st.checkbox("Douleur à la poitrine (thoracique) ?")
            choc = st.checkbox("Teint grisâtre, moite ou basse pression ?")
    
    if détresse or confusion or douleur_c or choc:
        er_redirect = True

    # 2. LOGIQUE SPÉCIFIQUE PAR PROTOCOLE
    else:
        # PNEUMONIE / MPOC
        if "Toux" in motif:
            st.info("Protocole OC-017 (Pneumonie) ou MPOC-EAMPOC")
            fievre = st.checkbox("Fièvre (> 38.5°C) ou frissons ?")
            comorbidite = st.checkbox("Comorbidité majeure (Cancer, Immunosuppression, Insuffisance cardiaque) ?")
            if comorbidite or fievre:
                trajectoire.update({"prof": "IPS", "temps": "45 min", "prix": 180.0})
            else:
                trajectoire.update({"prof": "Infirmière (OC)", "temps": "30 min", "prix": 95.0})

        # PHARYNGITE
        elif "Gorge" in motif:
            st.info("Protocole Pharyngite-amygdalite")
            if st.checkbox("Difficulté sévère à avaler sa salive ou à ouvrir la bouche ?"):
                er_redirect = True
            else:
                trajectoire.update({"prof": "Infirmière (Test rapide)", "temps": "20 min", "prix": 95.0})

        # INFECTION URINAIRE
        elif "Infection urinaire" in motif:
            sexe = st.radio("Sexe :", ["Femme", "Homme"])
            if sexe == "Homme":
                trajectoire.update({"prof": "IPS (Toujours complexe chez l'homme)", "prix": 138.0})
            else:
                if st.checkbox("Grossesse, fièvre ou douleur au dos ?"):
                    trajectoire.update({"prof": "IPS (Prioritaire)", "prix": 138.0})
                else:
                    trajectoire.update({"prof": "Infirmière (OC)", "prix": 95.0})

        # LYME
        elif "Lyme" in motif:
            st.info("Prophylaxie post-exposition (PPE)")
            tique_36h = st.checkbox("Tique attachée depuis plus de 36h ?")
            moins_72h = st.checkbox("Piqûre survenue il y a moins de 72h ?")
            if age >= 8 and tique_36h and moins_72h:
                trajectoire.update({"prof": "Infirmière (OC - Doxycycline)", "prix": 95.0})
            else:
                trajectoire.update({"prof": "IPS", "prix": 138.0})

        # SANTÉ SEXUELLE (Écoulement / Pertes / ITSS)
        elif any(x in motif for x in ["Écoulement", "Pertes", "Chlamydia"]):
            st.info("Protocoles ITSS / Pertes vaginales")
            if st.checkbox("Douleur abdominale basse, fièvre ou douleur testiculaire ?"):
                trajectoire.update({"prof": "IPS (Consultation curative)", "prix": 138.0})
            else:
                trajectoire.update({"prof": "Infirmière (Dépistage)", "prix": 95.0})

        # HTA
        elif "HTA" in motif:
            if st.checkbox("Pression >= 180/110 ou symptômes (vision floue, céphalée intense) ?"):
                er_redirect = True
            else:
                trajectoire.update({"prof": "Infirmière (Suivi/Ajustement)", "prix": 95.0})

    # 3. AFFICHAGE FINAL
    if er_redirect:
        st.critical("🚨 **ACTION REQUISE : NE PAS RÉSERVER.** Diriger le patient immédiatement vers l'URGENCE ou appeler le 911.")
    elif trajectoire["prix"] > 0:
        st.divider()
        c1, c2, c3 = st.columns(3)
        c1.metric("Professionnel", trajectoire["prof"])
        c2.metric("Temps", trajectoire["temps"])
        
        # Calcul financier final
        frais_base = trajectoire["prix"]
        f_ouverture = 35.0 if nouveau else 0.0
        total = frais_base + f_ouverture
        if "SAAQ" in motif:
            total *= 1.14975
            st.caption("Taxes incluses (Service administratif SAAQ)")
        else:
            st.caption("Service médical exonéré de taxes")

        c3.metric("Total à payer", f"{total:.2f} $")
