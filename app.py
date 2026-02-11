import streamlit as st

# Configuration de la page et style uniforme
st.set_page_config(page_title="Triage Clinique IPS Santé Plus", layout="wide")
st.markdown("""
    <style>
    html, body, [class*="css"], [class*="st-"] {
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🏥 Assistant Triage - Clinique IPS Santé Plus")

# --- ÉTAPE 1 : ACCUEIL ET DIVULGATION ---
st.subheader("1️⃣ Accueil et Informations Légales")
col_adm1, col_adm2 = st.columns(2)

with col_adm1:
    # Identification et frais d'ouverture [cite: 2-4, 8]
    dossier = st.radio("Avez-vous un dossier à la clinique ?", ["Oui", "Non"], horizontal=True)
    frais_ouv = 35.0 if dossier == "Non" else 0.0 [cite: 4]
    
    # Divulgations obligatoires 
    privé = st.toggle("Le patient sait que c'est une CLINIQUE PRIVÉE (frais à sa charge) ?") [cite: 5]
    pas_medecin = st.toggle("Le patient sait qu'il n'y a PAS DE MÉDECIN (IPS et infirmière uniquement) ?") [cite: 6]

with col_adm2:
    # Localisation et services [cite: 10-12]
    lieu = st.selectbox("Point de service :", ["-- Choisir --", "Jonquière", "Saint-Félicien"])

# --- DÉBLOCAGE DU TRIAGE ---
if privé and pas_medecin and lieu != "-- Choisir --":
    st.divider()
    st.subheader("2️⃣ Analyse du besoin (Recherche par mot-clé)")
    # Boîte de recherche avec banque de mots [cite: 13]
    recherche = st.text_input("Tapez le symptôme ou le type de consultation :").lower()

    if recherche:
        t = {"prof": "IPS", "temps": "30", "prix": 0.0, "depot": 0.0, "annul": "48h", "est_sm": False, "est_tda": False}
        
        # --- MODULE SANTÉ MENTALE (IPSSM) ---
        sm_keywords = ["mentale", "anxiété", "dépression", "sommeil", "alimentaire", "burnout", "deuil", "épuisement", "tda", "tdah"]
        if any(x in recherche for x in sm_keywords):
            t["est_sm"] = True [cite: 14]
            t["annul"] = "72h" [cite: 63]
            
            # Sécurité et Âge [cite: 15-20]
            st.error("🚨 SÉCURITÉ : Avez-vous des intentions de faire du mal à vous ou à autrui actuellement ?") [cite: 15]
            if st.radio("Réponse :", ["Non", "Oui"]) == "Oui":
                st.error("🚨 ACTION : Composez le 911 ou présentez-vous à l'urgence.") [cite: 16]
            elif st.number_input("Âge :", 0, 115, 18) < 18:
                st.warning("Désolé, nous ne traitons pas la clientèle de moins de 18 ans.") [cite: 19]
            else:
                # Informations obligatoires IPSSM [cite: 27-37, 66]
                est_tda = any(x in recherche for x in ["tda", "tdah"]) [cite: 21]
                with st.expander("📝 Informations obligatoires IPSSM", expanded=True):
                    pts = ["1. Téléconsultation (50 min)", "2. Approche personnalisée", "3. Antécédents", "4. Investigations", "5. Diagnostics", "6. Médication", "7. Arrêts travail", "8. Coût 250$", "9. Suivis 195$", "10. Dépôt 100$", "11. Lien Telus", "12. Questionnaire"]
                    st.markdown("\n".join([p for i, p in enumerate(pts) if not (est_tda and i in [0, 7])])) [cite: 23-37]

                if est_tda:
                    t.update({"prof": "Infirmière + IPSSM", "temps": "1h + 50min", "prix": 195.0, "prix_ipssm": 250.0, "depot": 100.0}) [cite: 23-25]
                else:
                    t.update({"prof": "IPSSM", "temps": "50", "prix": 250.0, "depot": 100.0}) [cite: 34, 36]

        # --- MODULE CONSULTATIONS SIMPLES / PROLONGÉES / COMPLEXES ---
        elif any(x in recherche for x in ["simple", "prolongée", "complexe", "suivi", "bilan"]):
            if "simple" in recherche:
                # 1 seul motif, sans avis IPS requis 
                st.info("💡 Consultation Simple : 1 seul motif.")
                t.update({"prof": "Infirmière", "prix": 140.0, "temps": "20", "annul": "24h"}) [cite: 39, 63]
            elif "prolongée" in recherche:
                # 2 motifs ou IPS nécessaire 
                st.info("💡 Consultation Prolongée : 2 motifs ou besoin d'expertise IPS.")
                t.update({"prof": "IPS", "prix": 180.0, "temps": "30", "annul": "48h"}) [cite: 39, 63]
            elif any(x in recherche for x in ["complexe", "bilan", "saaq"]):
                # Bilans, SAAQ, dossiers lourds [cite: 51, 53, 54]
                st.info("💡 Consultation Complexe : Bilan de santé, SAAQ ou hormones.")
                prix_bilan = 395.0 if dossier == "Non" else 345.0
                t.update({"prof": "IPS", "prix": prix_bilan, "temps": "45-60", "annul": "48h"})

        # --- MODULE URGENCE MINEURE (Aide-mémoire) ---
        else:
            # Trajectoires selon l'Aide-mémoire [cite: 38-48]
            if any(x in recherche for x in ["urine", "gorge", "oreille", "sinus"]):
                est_ips = st.checkbox("Le patient présente-t-il une contre-indication IPS ?") [cite: 38]
                t.update({"prof": "IPS" if est_ips else "Infirmière", "prix": 180.0 if est_ips else 140.0, "annul": "48h" if est_ips else "24h"}) [cite: 39, 42]
            
            # Gestion des prélèvements 
            if lieu == "Jonquière" and st.checkbox("Prélèvement requis ? (+35$)"): t["prix"] += 35.0 [cite: 38]
            elif lieu == "Saint-Félicien": st.warning("⚠️ Aucun prélèvement possible (sauf Strep-test).") [cite: 38]

        # --- ÉTAPE 3 : CONCLUSION ET SCRIPT ---
        if t["prix"] > 0:
            st.divider()
            st.subheader("3️⃣ Conclusion de l'appel")
            
            total = t["prix"] + frais_ouv
            msg_ouv = f" (incluant les frais d'ouverture de dossier de 35$)" if dossier == "Non" else "" [cite: 4]
            
            # Modes de paiement [cite: 67-69]
            if t["est_sm"]: paiement = "par téléphone par carte de crédit seulement" [cite: 69]
            elif lieu == "Jonquière": paiement = "par carte débit, carte de crédit ou argent comptant" [cite: 68]
            else: paiement = "par carte débit ou carte de crédit seulement" [cite: 67]

            script = f"""
            > "La durée de votre rendez-vous sera de **{t['temps']} minutes**. [cite: 61]
            > Nous ne traiterons que votre problème mentionné, tout ajout peut entraîner des frais. [cite: 62]
            > 
            > **Frais et Annulation :**
            > * Le coût est de **{total:.2f} $**{msg_ouv}. [cite: 4, 34]
            > * {'Un dépôt de 100$ est requis pour l\'IPSSM.' if t['depot'] > 0 else ''} [cite: 36]
            > * Le paiement se fera **{paiement}**. [cite: 67-69]
            > * Frais de **50%** en cas d'absence ou d'annulation moins de **{t['annul']}** avant. [cite: 63]
            > 
            > **Ponctualité :**
            > * Veuillez vous {'connecter' if t['est_sm'] else 'présenter'} **5 à 10 minutes à l'avance**. [cite: 64]
            > * Un retard de **10 minutes** est considéré comme une absence." [cite: 65]
            """
            st.info(script)
