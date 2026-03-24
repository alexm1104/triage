import streamlit as st

# Configuration de la page
st.set_page_config(page_title="Triage IPS Santé Plus", page_icon="🏥", layout="centered")

# Style CSS pour améliorer l'apparence
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stAlert { border-radius: 10px; }
    .price-box { 
        padding: 20px; 
        border-radius: 10px; 
        text-align: center; 
        font-size: 24px; 
        font-weight: bold;
        margin-top: 20px;
    }
    .simple { background-color: #e8f5e9; border: 2px solid #27ae60; color: #2e7d32; }
    .prolongee { background-color: #fff3e0; border: 2px solid #f39c12; color: #e65100; }
    .complexe { background-color: #ffebee; border: 2px solid #e74c3c; color: #c62828; }
    .exclusion { background-color: #212121; border: 2px solid #000; color: #ffffff; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏥 Triage Stratégique - IPS Santé Plus")
st.write("Outil d'aide à la décision pour la réception.")

# --- SECTION 1 : FILTRES DE BASE ---
st.subheader("1. Questions Filtres")
col1, col2 = st.columns(2)
with col1:
    plus_3_mois = st.checkbox("Problème chronique / + de 3 mois ?")
    examen_gyneco = st.checkbox("Examen gynéco (PAP test) requis ?")
with col2:
    est_bebe = st.checkbox("Évaluation globale bébé (sans problème)")
    autre_contraception = st.checkbox("Souhaite une nouvelle contraception (si stérilet)")

# --- SECTION 2 : MOTIFS DE CONSULTATION ---
st.subheader("2. Motifs de consultation")

# Catégories pour le triage
simples = st.multiselect("Motifs SIMPLES :", 
    ["ORL (Otite, Sinusite, Gorge)", "Toux < 3 sem / Asthme contrôlé", "Peau < 2 sem (Acné, Eczéma)", 
     "Infection urinaire (Femme 14+ simple)", "Retrait Stérilet"])

prolonges = st.multiselect("Motifs PROLONGÉS :", 
    ["Digestif (Ventre, Brûlements, Diarrhée)", "MSK Aigu (Douleur < 3 mois)", "Pression (Haute/Basse)", 
     "Céphalée / Mal de tête", "Urinaire (Homme, Enfant, Enceinte, Récidive)", "Abcès"])

complexes = st.multiselect("Motifs COMPLEXES :", 
    ["Cardio (Palpitations, Arythmie, Serrement)", "Bilan (Fatigue, Perte poids, Tremblements)", 
     "Hormonal (Ménopause, Infertilité)", "Migraine Chronique", "Dysfonction érectile", "Perte de cheveux"])

exclusions = st.multiselect("⚠️ EXCLUSIONS (Ne pas prendre) :", 
    ["Tunnel Carpien", "Nerf d'Arnold", "Kyste de Baker", "Bursite Coude/Épaule", "Écoulement des seins"])

# --- LOGIQUE DE CALCUL ---
if st.button("Générer le diagnostic de triage"):
    
    # 1. Gestion des exclusions
    if exclusions:
        st.markdown('<div class="price-box exclusion">REFUS : SERVICE NON OFFERT</div>', unsafe_allow_html=True)
        st.error(f"Nous ne traitons pas : {', '.join(exclusions)}. Référer au public ou spécialiste externe.")
    
    else:
        type_consu = "simple"
        prix_min, prix_max = 140, 180
        extras = 0
        notes = []

        # Calcul des extras
        if "Retrait Stérilet" in simples:
            extras += 55
            notes.append("⚠️ Retrait stérilet : Prendre Tylénol 1h avant.")
            if autre_contraception:
                prix_min, prix_max = 245, 245 # Prix fixe selon procédure
            else:
                prix_min, prix_max = 175, 175 # 175 + 55 = 230 total
        
        if "Abcès" in prolonges:
            extras += 55
        
        if examen_gyneco:
            extras += 35
            notes.append("Prévoir frais de prélèvement (+35$).")

        # Détermination du type
        nb_simples = len(simples)
        
        if complexes or plus_3_mois:
            type_consu = "complexe"
            prix_min, prix_max = 245, 310
        elif prolonges or nb_simples > 1 or examen_gyneco or est_bebe:
            type_consu = "prolongee"
            prix_min, prix_max = 175, 195
            if est_bebe: prix_min, prix_max = 195, 195
        
        # Affichage du résultat
        css_class = type_consu
        st.markdown(f'<div class="price-box {css_class}">Consultation {type_consu.upper()}</div>', unsafe_allow_html=True)
        
        total_min = prix_min + extras
        total_max = prix_max + extras
        
        if total_min == total_max:
            st.info(f"**Prix fixe : {total_min}$**")
        else:
            st.info(f"**Échelle de prix : {total_min}$ à {total_max}$**")

        # Instructions spécifiques
        st.subheader("Instructions pour le patient :")
        col_a, col_b = st.columns(2)
        with col_a:
            st.write("**Politiques :**")
            st.write("- Annulation : 72h (Bilans) / 24h (Régulier)")
            st.write("- Retard : 10 min (Bilans) / 5 min (Autres)")
        with col_b:
            st.write("**Santé :**")
            st.write("- Masque obligatoire si symptômes")
            st.write("- Arriver 15 min avant si test COVID requis")

        for note in notes:
            st.warning(note)

        if "Céphalée / Mal de tête" in prolonges:
            st.warning("👤 Dossier à référer à Kévin.")
        if "ORL (Otite, Sinusite, Gorge)" in simples:
            st.write("💡 Note : Un seul motif traité par rendez-vous (15 min).")
