import streamlit as st

# Configuration de la page
st.set_page_config(page_title="Triage IPS Santé Plus", page_icon="🏥", layout="wide")

st.title("🏥 Assistant Expert de Triage - IPS Santé Plus")

# --- ÉTAPE 1 : IDENTIFICATION PRÉALABLE ---
st.subheader("1️⃣ Informations Préliminaires")
col_init1, col_init2 = st.columns(2)

with col_init1:
    point_service = st.selectbox("Pour quelle clinique est la demande ?", 
                                ["-- Sélectionner --", "Jonquière", "Saint-Félicien"])
with col_init2:
    deja_dossier = st.selectbox("Le client a-t-il déjà un dossier chez nous ?", 
                               ["-- Sélectionner --", "Oui", "Non"])

# On ne débloque la suite que si les deux premières questions sont répondues
if point_service != "-- Sélectionner --" and deja_dossier != "-- Sélectionner --":
    
    st.divider()
    
    # --- ÉTAPE 2 : LE TRIAGE CLINIQUE ---
    st.subheader("2️⃣ Analyse du besoin")
    
    with st.sidebar:
        st.header("👤 Détails Patient")
        age = st.number_input("Âge du patient", min_value=0, max_value=115, value=18)
        st.write(f"📍 Clinique : **{point_service}**")
        st.write(f"📂 Dossier existant : **{deja_dossier}**")
        st.divider()
        st.caption("© Clinique IPS Santé Plus 2026")

    motif = st.selectbox("Quel est le motif de l'appel ?", [
        "-- Choisir un motif --",
        "Urinaire : Brûlure/Inconfort (Infection - OC-001)",
        "ORL : Mal de gorge (Pharyngite - OC-004)",
        "ORL : Douleur à l'oreille (Otite)",
        "Respiratoire : Toux / Fièvre / Pneumonie (OC-017)",
        "Dermato : Plaques rouges / Cellulite / Zona",
        "Santé Mentale : Évaluation initiale IPSSM (Adultes seulement)",
        "Santé Mentale : Suivi IPSSM",
        "Bilan Hormonal (Protocole Demers)",
        "Bilan de Santé complet (Check-up)",
        "Examen SAAQ (Conducteur)",
        "Soins infirmiers : Lavage d'oreilles / Injection"
    ])

    if motif != "-- Choisir un motif --":
        # Valeurs par défaut (IPS 180$ / Inf 140$ selon vos documents récents)
        trajectoire = {"prof": "IPS", "temps": "30 min", "prix": 180.0, "taxable": False, "note": ""}
        rediriger_urgence = False

        # --- FILTRE DE SÉCURITÉ ---
        with st.expander("🚨 FILTRE ROUGE (À vérifier immédiatement)", expanded=True):
            er_check = st.checkbox("Signes de gravité (Détresse respiratoire, douleur thoracique, confusion, idées noires)")
        
        if er_check:
            rediriger_urgence = True
        else:
            # LOGIQUE SPÉCIFIQUE
            if "Mentale" in motif:
                if age < 18:
                    st.error("❌ L'IPSSM ne voit que les ADULTES (18 ans +).")
                    trajectoire["prix"] = 0
                else:
                    prix_sm = 395.0 if "Évaluation" in motif else 250.0
                    trajectoire.update({"prof": "IPSSM (Télémédecine)", "prix": prix_sm})

            elif "SAAQ" in motif:
                visite_2ans = st.radio("Visite médicale à la clinique < 2 ans ?", ["Non", "Oui"])
                if visite_2ans == "Oui":
                    trajectoire.update({"prof": "IPS", "prix": 198.99, "taxable": True})
                else:
                    st.error("Action : Impossible sans visite récente. Proposer un Bilan de Santé d'abord.")
                    trajectoire["prix"] = 0

            elif "Bilan de Santé" in motif:
                prix_bilan = 345.0 if deja_dossier == "Oui" else 395.0
                trajectoire.update({"prof": "IPS", "temps": "45-60 min", "prix": prix_bilan})

            elif "Urinaire" in motif or "Pharyngite" in motif:
                if st.checkbox("Signes de complication (Homme, Fièvre au dos, Grossesse) ?"):
                    trajectoire.update({"prof": "IPS", "prix": 180.0})
                else:
                    trajectoire.update({"prof": "Infirmière (OC)", "prix": 140.0})

        # --- RÉSULTAT ET SOMMAIRE DE FIN D'APPEL ---
        if rediriger_urgence:
            st.critical("🚨 **NE PAS PRENDRE DE RENDEZ-VOUS.** Diriger vers l'urgence ou le 911.")
        elif trajectoire["prix"] > 0:
            st.divider()
            
            # Calcul financier
            frais_ouv = 35.0 if deja_dossier == "Non" else 0.0
            total_ht = trajectoire["prix"] + frais_ouv
            total_final = total_ht * 1.14975 if trajectoire["taxable"] else total_ht
            
            # --- LE SCRIPT DE LA SECRÉTAIRE ---
            st.subheader("💬 Script de fin d'appel (À lire au patient)")
            
            script_text = f"""
            > "Parfait, j'ai bien noté. Je vous ai réservé un rendez-vous à notre clinique de **{point_service}**. 
            > Vous serez vu par notre **{trajectoire['prof']}** pour une durée d'environ **{trajectoire['temps']}**.
            > 
            > **Détails importants :**
            > * Le montant total sera de **{total_final:.2f} $** (incluant les frais d'ouverture de dossier de 35$ et taxes s'il y a lieu).
            > * Veuillez apporter votre liste de médicaments à jour.
            > * Arrivez 10 minutes à l'avance pour finaliser votre dossier.
            """
            
            if "Télémédecine" in trajectoire["prof"]:
                script_text += "\n> * Note : Puisque c'est en télémédecine, vous recevrez un lien par courriel 15 minutes avant l'heure."
            
            st.markdown(script_text)
            
            with st.expander("📊 Détail technique pour facturation"):
                st.write(f"Prix de base : {trajectoire['prix']:.2f} $")
                st.write(f"Frais d'ouverture : {frais_ouv:.2f} $")
                st.write("Taxes : " + ("Appliquées (SAAQ)" if trajectoire["taxable"] else "Exonéré"))

else:
    st.info("Veuillez répondre aux deux questions ci-dessus pour commencer le triage.")
