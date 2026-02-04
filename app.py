import streamlit as st

# Configuration de l'application
st.set_page_config(page_title="Triage IPS Santé Plus", page_icon="🏥", layout="wide")

st.title("🏥 Assistant Triage & Gestion - IPS Santé Plus")

# --- ÉTAPE 1 : IDENTIFICATION (En haut de la page pour bloquer la suite) ---
st.subheader("1️⃣ Accueil")
col_id1, col_id2 = st.columns(2)
with col_id1:
    pt_service = st.selectbox("Clinique :", ["-- Sélectionner --", "Jonquière", "Saint-Félicien"])
with col_id2:
    statut_dossier = st.selectbox("Dossier existant ?", ["-- Sélectionner --", "Oui", "Non"])

if pt_service != "-- Sélectionner --" and statut_dossier != "-- Sélectionner --":
    
    # Création des onglets pour organiser le travail de la secrétaire
    tab1, tab2, tab3 = st.tabs(["🔍 Triage Clinique", "💰 Facturation", "📋 Checklist & Script"])

    with tab1:
        st.subheader("Analyse du besoin")
        recherche = st.text_input("Tapez le symptôme (ex: oreille, urine, mentale, bilan) :").lower()
        
        # Initialisation des variables de trajectoire
        t = {"prof": "À déterminer", "prix": 0.0, "delai_annul": "24h", "note": ""}
        redir_er = False

        if recherche:
            # LOGIQUE DE TRIAGE (Exemple condensé avec vos règles)
            if any(x in recherche for x in ["mentale", "hormonal", "bilan", "métabolique"]):
                t.update({"prof": "IPS / Spécialisé", "prix": 350.0, "delai_annul": "72h"})
                if "mentale" in recherche: t["note"] = "Télémédecine (18 ans +)."
            
            elif any(x in recherche for x in ["urine", "gorge", "oreille", "toux", "lyme"]):
                # Distinction simplifiée Infirmière vs IPS
                if st.checkbox("Signes de complication ou critères d'exclusion IPS ?"):
                    t.update({"prof": "IPS", "prix": 180.0, "delai_annul": "48h"})
                else:
                    t.update({"prof": "Infirmière (OC)", "prix": 140.0, "delai_annul": "24h"})
            
            elif "saaq" in recherche:
                t.update({"prof": "IPS", "prix": 198.99, "delai_annul": "48h"})

            st.success(f"Professionnel recommandé : **{t['prof']}**")

    with tab2:
        st.subheader("Détails financiers")
        frais_ouv = 35.0 if statut_dossier == "Non" else 0.0
        sous_total = t["prix"] + frais_ouv
        # Note : La taxe ne s'applique que si c'est la SAAQ (donnée simplifiée ici)
        total_final = sous_total * 1.14975 if "saaq" in recherche else sous_total
        
        col_f1, col_f2 = st.columns(2)
        col_f1.metric("Total à percevoir", f"{total_final:.2f} $")
        col_f2.write(f"**Modes de paiement acceptés :**\n* Argent\n* Débit\n* Crédit")

    with tab3:
        st.subheader("Conclusion de l'appel")
        
        # --- SCRIPT AUTOMATISÉ ---
        st.info("💬 **Script à lire au patient :**")
        script = f"""
        "C'est confirmé pour votre rendez-vous à **{pt_service}**. 
        Vous serez vu par notre **{t['prof']}**. 
        
        Le montant total est de **{total_final:.2f} $**.
        
        **Politiques de la clinique :**
        * Veuillez vous présenter **10 minutes à l'avance** pour finaliser votre dossier.
        * Notez que tout retard de plus de **10 minutes** sera considéré comme une absence.
        * Votre délai d'annulation est de **{t['delai_annul']}**. 
        * En cas d'annulation hors délai ou d'absence, des frais de **50% de la consultation** seront chargés lors de votre prochain passage."
        """
        st.markdown(script)

        # --- CHECKLIST ADMINISTRATIVE ---
        st.divider()
        st.subheader("✅ Checklist Secrétaire")
        c1, c2 = st.columns(2)
        with c1:
            st.checkbox("A validé le mode de paiement (Argent/Débit/Crédit)")
            st.checkbox(f"A bien mentionné le délai de {t['delai_annul']}")
        with c2:
            st.checkbox("A mentionné la règle du 10 min de retard")
            st.checkbox("A mentionné les frais de 50% pour absence")

else:
    st.warning("Veuillez identifier le point de service et le statut du dossier pour commencer.")
