# --- MODULE RECHERCHE INTELLIGENTE ---
symptome_saisi = st.text_input("Tapez le symptôme (ex: oreille, gorge, urine) :").lower()

if "oreille" in symptome_saisi:
    st.info("👂 **Protocole Oreille détecté (OC-006 / OC-014)**")
    
    # 1. Questions d'exclusion (Vers IPS)
    st.subheader("Vérification des critères d'exclusion")
    col1, col2 = st.columns(2)
    with col1:
        vertige = st.checkbox("Vertiges ou perte d'équilibre ?")
        ecoulement = st.checkbox("Écoulement de pus ou sang ?")
    with col2:
        trauma = st.checkbox("Suite à un choc ou objet inséré ?")
        fievre_longue = st.checkbox("Fièvre persistante > 48h ?")

    # 2. Identification du type d'otite
    externe = st.toggle("La douleur augmente en touchant/tirant l'oreille ? (Signe d'otite externe)")

    # 3. Résultat de l'aiguillage
    if vertige or ecoulement or trauma or fievre_longue:
        st.warning("⚠️ **Trajectoire : IPS.** Le cas présente des critères d'exclusion pour l'infirmière.")
        trajectoire_finale = "IPS"
    elif externe:
        st.success("✅ **Trajectoire : Infirmière (OC-014 - Otite Externe).**")
        trajectoire_finale = "Infirmière"
    else:
        st.success("✅ **Trajectoire : Infirmière (OC-006 - Otite Moyenne).**")
        trajectoire_finale = "Infirmière"
