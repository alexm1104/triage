import streamlit as st

# 1. Configuration et style
st.set_page_config(page_title="Triage Clinique IPS Santé Plus", layout="wide")

st.markdown("""
    <style>
    html, body, [class*="css"], [class*="st-"] {
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif !important;
    }
    .stAlert { border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏥 Assistant Triage Expert - IPS Santé Plus")

# --- ÉTAPE 1 : ACCUEIL ET DIVULGATION ---
st.subheader("1️⃣ Accueil et Informations Légales")
col_adm1, col_adm2 = st.columns(2)

with col_adm1:
    dossier = st.radio("Avez-vous un dossier à la clinique ?", ["Oui", "Non"], horizontal=True)
    privé = st.toggle("Le patient sait que c'est une CLINIQUE PRIVÉE (frais à sa charge) ?")
    pas_medecin = st.toggle("Le patient sait qu'il n'y a PAS DE MÉDECIN (IPS/Inf uniquement) ?")

with col_adm2:
    lieu = st.selectbox("Point de service :", ["-- Choisir --", "Jonquière", "Saint-Félicien"])

# --- DÉBLOCAGE DU TRIAGE ---
if privé and pas_medecin and lieu != "-- Choisir --":
    st.divider()
    st.subheader("2️⃣ Analyse du besoin (Recherche par mot-clé)")
    recherche = st.text_input("Tapez le symptôme (ex: oreille, gorge, urine, mentale, saaq) :").lower()

    if recherche:
        # Initialisation des variables
        t = {"prof": "À déterminer", "temps": "30", "prix": 0.0, "depot": 0.0, "annul": "48h", "est_sm": False, "est_tda": False, "prix_ipssm": 0.0, "note": ""}
        frais_ouv = 35.0 if dossier == "Non" else 0.0
        
        # --- MODULE SANTÉ MENTALE (IPSSM) ---
        if any(x in recherche for x in ["mentale", "anxiété", "dépression", "sommeil", "tda", "tdah", "burnout"]):
            t["est_sm"] = True
            t["annul"] = "72h"
            t["est_tda"] = any(x in recherche for x in ["tda", "tdah"])
            
            st.error("🚨 SÉCURITÉ : Avez-vous des intentions de faire du mal à vous ou à autrui ?")
            if st.radio("Réponse :", ["Non", "Oui"]) == "Oui":
                st.error("🚨 ACTION : Composez le 911 ou allez à l'urgence.")
            elif st.number_input("Âge :", 0, 115, 18) < 18:
                st.warning("Désolé, nous ne voyons que les adultes (18+) en santé mentale.")
            else:
                points = [
                    "1. Téléconsultation avec l’IPSSM d’une durée de 50 min.", "2. Approche personnalisée.", "3. Validation des antécédents.", 
                    "4. Investigations nécessaires.", "5. Pose les diagnostics.", "6. Prescrit/ajuste médication.", 
                    "7. Arrêts de travail si nécessaire.", "8. Coût de 250$ (1ère consult).", "9. Suivis 20 min à 195$.", 
                    "10. Dépôt de 100$ requis.", "11. Lien Telus Santé par courriel.", "12. Questionnaire à remplir avant le RDV."
                ]
                with st.expander("📝 Informations obligatoires IPSSM", expanded=True):
                    st.markdown("\n".join([p for i, p in enumerate(points) if not (t["est_tda"] and i in [0, 7])]))

                if t["est_tda"]:
                    t.update({"prof": "Infirmière + IPSSM", "temps": "1h (Inf) + 50min (IPSSM)", "prix": 195.0, "prix_ipssm": 250.0, "depot": 100.0})
                else:
                    t.update({"prof": "IPSSM (Télémédecine)", "temps": "50", "prix": 250.0, "depot": 100.0})

        # --- MODULE OREILLE (OTITE) ---
        elif any(x in recherche for x in ["oreille", "otite", "entendre"]):
            st.info("👂 **Évaluation de l'oreille (Aide-mémoire : Otite)**")
            st.markdown("**Posez les questions de gravité :**")
            col1, col2 = st.columns(2)
            with col1:
                q1 = st.checkbox("Le patient a-t-il des vertiges ou des pertes d'équilibre ?")
                q2 = st.checkbox("Y a-t-il un écoulement de pus ou de sang important ?")
            with col2:
                q3 = st.checkbox("La douleur fait-elle suite à un choc ou un objet inséré ?")
                q4 = st.checkbox("Le patient fait-il de la fièvre (>38.5) depuis plus de 48h ?")
            
            if q1 or q2 or q3 or q4:
                t.update({"prof": "IPS (Cas complexe)", "prix": 180.0, "annul": "48h", "temps": "30", "note": "Cas d'exclusion pour l'infirmière."})
            else:
                t.update({"prof": "Infirmière (Otite simple)", "prix": 140.0, "annul": "24h", "temps": "20"})

        # --- MODULE URINAIRE ---
        elif any(x in recherche for x in ["urine", "brulure", "vessie"]):
            st.info("💧 **Évaluation Urinaire (Aide-mémoire : Infection)**")
            st.markdown("**Vérifiez les critères d'exclusion IPS :**")
            if st.checkbox("Le patient est-il un Homme, une Femme enceinte ou a-t-il mal au dos + fièvre ?"):
                t.update({"prof": "IPS", "prix": 180.0, "annul": "48h"})
            else:
                t.update({"prof": "Infirmière (OC-001)", "prix": 140.0, "annul": "24h"})

        # --- AUTRES MOTIFS (À compléter selon la même structure) ---
        else:
            t.update({"prof": "IPS", "prix": 180.0, "annul": "48h", "temps": "30"})
            if lieu == "Jonquière" and st.checkbox("Prélèvement requis ? (+35$)"):
                t["prix"] += 35.0

        # --- ÉTAPE 3 : CONCLUSION ---
        if t["prix"] > 0:
            st.divider()
            st.subheader("3️⃣ Conclusion de l'appel")
            
            total = t["prix"] + frais_ouv
            msg_ouv = f" (incluant les frais d'ouverture de dossier de 35$)" if dossier == "Non" else ""
            paiement = "**par téléphone par carte de crédit seulement**" if t["est_sm"] else ("par débit, crédit ou argent" if lieu == "Jonquière" else "par débit ou crédit seulement")

            if t["est_tda"]:
                texte_prix = f"Le coût est de **{total:.2f} $**{msg_ouv} pour l'infirmière et **250.00 $** pour l'IPSSM."
            else:
                texte_prix = f"Le coût de la consultation est de **{total:.2f} $**{msg_ouv}."

            script = f"""
            > **Script de fin :**
            > "La durée de votre rendez-vous sera de **{t['temps']} minutes**. Nous ne traiterons que votre problème mentionné.
            > 
            > * {texte_prix}
            > * {'Un dépôt de 100$ est requis pour l\'IPSSM.' if t['depot'] > 0 else ''}
            > * Le paiement se fera {paiement}.
            > * Politique d'annulation : **{t['annul']}** d'avance, sinon **50% des frais** seront chargés.
            > * Arrivez **5 à 10 min** d'avance. Un retard de **10 min** est une absence."
            """
            st.info(script)
