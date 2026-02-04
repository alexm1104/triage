import streamlit as st

# Configuration de base
st.set_page_config(page_title="Triage IPS Santé Plus", page_icon="🏥", layout="wide")

st.title("🏥 Système de Triage Expert - Clinique IPS Santé Plus")
st.caption("Intelligence Clinique basée sur les OC-001 à OC-020 et Protocoles Internes")

# --- ÉTAPE 1 : IDENTIFICATION ADMINISTRATIVE ---
st.subheader("1️⃣ Accueil et Identification")
col_adm1, col_adm2 = st.columns(2)

with col_adm1:
    point_service = st.selectbox("Clinique visée :", ["-- Sélectionner --", "Jonquière", "Saint-Félicien"])
with col_adm2:
    deja_dossier = st.selectbox("Le patient a-t-il déjà un dossier chez nous ?", ["-- Sélectionner --", "Oui", "Non"])

# Déblocage de la suite uniquement si l'étape 1 est complétée
if point_service != "-- Sélectionner --" and deja_dossier != "-- Sélectionner --":
    st.divider()
    
    # --- ÉTAPE 2 : RECHERCHE PAR MOT-CLÉ ---
    st.subheader("2️⃣ Analyse du besoin (Triage)")
    recherche = st.text_input("Tapez le symptôme ou motif (ex: oreille, urine, gorge, mentale, saaq) :").lower()

    if recherche:
        # Variables de calcul par défaut
        t = {"prof": "IPS", "temps": "30 min", "prix": 180.0, "taxe": False, "note": "", "script": ""}
        frais_ouv = 35.0 if deja_dossier == "Non" else 0.0
        redir_er = False

        # --- FILTRE DE SÉCURITÉ UNIVERSEL ---
        with st.expander("🚨 VÉRIFICATION DES DRAPEAUX ROUGES", expanded=True):
            st.warning("Si l'un de ces points est coché, dirigez vers l'URGENCE (911).")
            er1 = st.checkbox("Difficulté respiratoire sévère ou étouffement")
            er2 = st.checkbox("Douleur thoracique subite ou malaise cardiaque")
            er3 = st.checkbox("Confusion, perte de conscience ou idées suicidaires")
        
        if er1 or er2 or er3:
            redir_er = True
        else:
            # --- LOGIQUE DES ORDONNANCES COLLECTIVES ---
            
            # URINAIRE (OC-001)
            if any(x in recherche for x in ["urine", "brulure", "vessie"]):
                st.info("💧 **Protocole Urinaire (OC-001)**")
                if st.checkbox("Homme, Femme enceinte, ou Douleur au dos + Fièvre ?"):
                    t.update({"prof": "IPS", "note": "Cas complexe ou risque de pyélonéphrite."})
                else:
                    t.update({"prof": "Infirmière (OC-001)", "prix": 140.0})

            # ORL (OC-004, 006, 014)
            elif any(x in recherche for x in ["gorge", "avaler", "amygdale"]):
                st.info("👄 **Protocole Pharyngite (OC-004)**")
                if st.checkbox("Incapable d'avaler sa salive ou voix étouffée ?"):
                    redir_er = True
                else:
                    t.update({"prof": "Infirmière (Test Strep)", "prix": 140.0})

            elif any(x in recherche for x in ["oreille", "otite"]):
                st.info("👂 **Protocole Otite (OC-006 / 014)**")
                if st.checkbox("Vertiges, écoulement de pus/sang ou traumatisme ?"):
                    t.update({"prof": "IPS", "note": "Exclusion OC : suspicion de perforation ou atteinte interne."})
                else:
                    t.update({"prof": "Infirmière", "prix": 140.0})

            # RESPIRATOIRE (OC-012, 015, 017)
            elif any(x in recherche for x in ["toux", "poumon", "fievre", "mpoc"]):
                st.info("🫁 **Protocole Respiratoire (OC-017 / 012)**")
                if st.checkbox("Fièvre persistante, essoufflement marqué ou MPOC connu ?"):
                    t.update({"prof": "IPS", "prix": 180.0})
                else:
                    t.update({"prof": "Infirmière", "prix": 140.0})

            # SANTÉ MENTALE (IPSSM)
            elif any(x in recherche for x in ["mentale", "tdah", "anxiete", "depression"]):
                st.info("🧠 **Protocole Santé Mentale (IPSSM)**")
                age = st.number_input("Âge du patient :", 0, 115, 18)
                if age < 18:
                    st.error("L'IPSSM ne voit que les adultes.")
                    t["prix"] = 0
                else:
                    eval_init = st.toggle("Est-ce une première évaluation ?")
                    prix_sm = 395.0 if eval_init else 250.0
                    t.update({"prof": "IPSSM (Télémédecine)", "prix": prix_sm, "temps": "60 min" if eval_init else "30 min"})

            # DERMATO (OC-008, 018)
            elif any(x in recherche for x in ["zona", "bulles", "peau"]):
                st.info("🧴 **Protocole Dermato / Zona (OC-008)**")
                if st.checkbox("Bulles sur le visage ou près de l'œil ?"):
                    redir_er = True
                else:
                    t.update({"prof": "IPS", "prix": 180.0})

            # LYME (OC-020)
            elif any(x in recherche for x in ["tique", "lyme"]):
                st.info("🕷️ **Protocole Lyme (OC-020)**")
                if st.checkbox("Tique attachée > 36h et retrait < 72h ?"):
                    t.update({"prof": "Infirmière (PPE)", "prix": 140.0})
                else:
                    t.update({"prof": "IPS", "prix": 180.0})

            # SAAQ
            elif "saaq" in recherche:
                st.info("🚗 **Examen Conducteur SAAQ**")
                if st.radio("Visite médicale < 2 ans ?", ["Non", "Oui"]) == "Oui":
                    t.update({"prof": "IPS", "prix": 198.99, "taxe": True})
                else:
                    st.error("Action : Doit passer un Bilan de Santé avant l'examen SAAQ.")
                    t["prix"] = 0

            # BILANS
            elif "bilan" in recherche:
                if "hormonal" in recherche or "demers" in recherche:
                    t.update({"prof": "IPS", "prix": 350.0, "note": "Patient doit être à jeun."})
                else:
                    t.update({"prof": "IPS", "prix": 395.0 if deja_dossier == "Non" else 345.0})

        # --- RÉSULTATS ET SCRIPT ---
        if redir_er:
            st.error("🚨 **ORIENTATION : URGENCE.** Ne pas prendre de rendez-vous.")
        elif t["prix"] > 0:
            st.divider()
            
            # Calcul financier
            total_ht = t["prix"] + frais_ouv
            total_ttc = (total_ht * 1.14975) if t["taxe"] else total_ht
            
            st.success(f"✅ **Trajectoire : {t['prof']}**")
            
            st.subheader("💬 Script à lire au patient :")
            script = f"""
            > "J'ai bien noté vos symptômes. Pour ce type de besoin, je vous ai réservé une consultation avec notre **{t['prof']}** à la clinique de **{point_service}**.
            > 
            > Le montant total de la rencontre sera de **{total_ttc:.2f} $** (incluant les frais d'ouverture de dossier et taxes si applicable).
            > 
            > **Consignes importantes :**
            > * {t['note'] if t['note'] else "Veuillez apporter votre liste de médicaments à jour."}
            > * Arrivez 10 minutes avant l'heure prévue.
            """
            st.markdown(script)
            
            with st.expander("Détail de la facturation"):
                st.write(f"Consultation : {t['prix']:.2f} $")
                st.write(f"Ouverture dossier : {frais_ouv:.2f} $")
                st.write("Taxes : " + ("14.975% (SAAQ)" if t["taxe"] else "Exonéré (Médical)"))

else:
    st.info("Veuillez sélectionner le lieu et le statut du dossier pour activer le triage.")
