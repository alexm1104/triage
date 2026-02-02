import streamlit as st

# Configuration de la page
st.set_page_config(page_title="Triage Clinique IPS Santé Plus", page_icon="🏥", layout="wide")

# --- STYLE ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stAlert { border-radius: 10px; }
    .stMetric { background-color: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

st.title("🏥 Assistant de Triage Intelligent - IPS Santé Plus")
st.caption("Outil basé sur les protocoles et ordonnances collectives de la clinique")

# --- DONNÉES PATIENT ---
with st.sidebar:
    st.header("👤 Patient")
    nom = st.text_input("Nom complet")
    age = st.number_input("Âge", min_value=0, max_value=115, value=18)
    point_service = st.radio("Lieu de consultation", ["Jonquière", "Saint-Félicien"])
    nouveau = st.checkbox("Nouveau patient (Frais d'ouverture 35$)")
    st.divider()
    st.write("© Clinique IPS Santé Plus")

# --- SÉLECTION DU MOTIF ---
st.subheader("🔍 Analyse du besoin")
motif = st.selectbox("Sélectionnez le motif principal :", [
    "-- Choisir --",
    "Urgence Mineure (Otite, gorge, urinaire, etc.)",
    "Toux / Suspicion Pneumonie (Protocole OC-017)",
    "Consultation Prolongée (Suivi complexe, PAP test)",
    "Bilan de Santé Complet",
    "Santé Mentale (Suivi/Renouvellement)",
    "Soins Infirmiers (Lavage d'oreilles, injection)",
    "Cardiologie (CardioSTAT / MAPA)"
])

# --- LOGIQUE CLINIQUE ET TARIFICATION ---
if motif != "-- Choisir --":
    trajectoire = {"prof": "À déterminer", "temps": "--", "prix": 0.0, "note": ""}
    
    # 1. Cas spécifique : Pneumonie (Basé sur OC-017) 
    if "Pneumonie" in motif:
        st.warning("⚠️ **VÉRIFICATION DES CONTRE-INDICATIONS (OC-017)**")
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            moins_14 = age < 14
            grossesse = st.checkbox("Grossesse ou allaitement")
            immuno = st.checkbox("Immunosuppression / Cancer / VIH")
        with col_c2:
            détresse = st.checkbox("Détresse respiratoire ou Confusion")
            bp = st.checkbox("Basse pression (TAS < 90 ou TAD < 60)")

        if moins_14 or grossesse or immuno or détresse or bp:
            st.error("❌ **CONTRE-INDICATION DÉCELÉE** : Ce patient ne peut être vu par l'infirmière sous l'ordonnance collective OC-017. Référer immédiatement à l'IPS ou à l'urgence.")
        else:
            st.success("✅ Éligible à l'évaluation infirmière (OC-017)")
            trajectoire.update({"prof": "Infirmière clinicienne", "temps": "30-45 min", "prix": 95.0, "note": "Appliquer le protocole d'appréciation physique."})

    # 2. Urgence Mineure 
    elif "Urgence Mineure" in motif:
        trajectoire.update({"prof": "IPS ou Infirmière", "temps": "20-30 min", "prix": 138.0, "note": "Infection urinaire, otite, gorge, ITSS."})

    # 3. Consultation Prolongée 
    elif "Consultation Prolongée" in motif:
        trajectoire.update({"prof": "IPS", "temps": "45 min", "prix": 180.0, "note": "Hypertension, MPOC, PAP test, douleur chronique."})

    # 4. Santé Mentale 
    elif "Santé Mentale" in motif:
        st.info("ℹ️ Rappel : L'IPS peut renouveler si l'état est stable. Pas de nouveau diagnostic TDAH.")
        trajectoire.update({"prof": "IPS", "temps": "30 min", "prix": 138.0})

    # 5. Soins Infirmiers [cite: 12, 16]
    elif "Soins Infirmiers" in motif:
        type_soin = st.selectbox("Type de soin :", ["Lavage d'oreilles", "Injection de médicament", "Cryothérapie"])
        prix_soin = 40.0 if "Cryothérapie" not in type_soin else 50.0
        trajectoire.update({"prof": "Infirmière", "temps": "30 min", "prix": prix_soin})

    # 6. Bilan de Santé 
    elif "Bilan de Santé" in motif:
        trajectoire.update({"prof": "IPS", "temps": "45-60 min", "prix": 350.0, "note": "Examen physique complet + prélèvements."})

    # --- AFFICHAGE DU RÉSULTAT FINAL ---
    if trajectoire["prix"] > 0:
        st.divider()
        res_col1, res_col2, res_col3 = st.columns(3)
        with res_col1:
            st.metric("Professionnel", trajectoire["prof"])
        with res_col2:
            st.metric("Durée", trajectoire["temps"])
        with res_col3:
            st.metric("Point de service", point_service)

        # Calcul financier
        frais_base = trajectoire["prix"]
        f_ouverture = 35.0 if nouveau else 0.0
        total_ht = frais_base + f_ouverture
        taxes = total_ht * 0.14975
        total_ttc = total_ht + taxes

        st.success(f"### TOTAL À PAYER : {total_ttc:.2f} $")
        with st.expander("Détails du calcul"):
            st.write(f"Consultation : {frais_base:.2f} $")
            if nouveau: st.write(f"Ouverture de dossier : {f_ouverture:.2f} $")
            st.write(f"Taxes (TPS/TVQ) : {taxes:.2f} $")
            if trajectoire["note"]: st.caption(f"Note : {trajectoire['note']}")
