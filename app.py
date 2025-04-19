import streamlit as st
import pandas as pd
from collections import Counter
import os
# -------- Load Local DataFrames --------
print(os.getcwd())
group_df = pd.read_csv("groups_with_associated_techniques.csv")
technique_df = pd.read_csv("technique_details.csv")

technique_df["technique_id"]=technique_df["technique_id"].str.strip(" ")

# -------- Helper Functions --------
def find_groups_using_technique(technique_id, group_df):
    matching_groups = []

    for _, row in group_df.iterrows():
        techniques = row['assoc_techniques']
        if isinstance(techniques, str):
            techniques = eval(techniques)
        if technique_id in techniques:
            matching_groups.append(row['group_name'])

    return matching_groups

def get_all_techniques_by_groups(group_names, group_df):
    all_techniques = []

    for _, row in group_df.iterrows():
        if row['group_name'] in group_names:
            techniques = row['assoc_techniques']
            if isinstance(techniques, str):
                techniques = eval(techniques)
            all_techniques.extend(techniques)

    return all_techniques

def filter_techniques_by_accuracy(techniques, group_names, group_df, threshold_percent):
    group_count = len(group_names)
    technique_counter = Counter()

    for _, row in group_df.iterrows():
        if row['group_name'] in group_names:
            techniques_in_group = row['assoc_techniques']
            if isinstance(techniques_in_group, str):
                techniques_in_group = eval(techniques_in_group)
            for tech in techniques_in_group:
                technique_counter[tech] += 1

    filtered_techniques = [
        tech for tech, count in technique_counter.items()
        if (count / group_count) * 100 >= threshold_percent
    ]

    return filtered_techniques

def get_technique_name(tech_id, technique_df):
    match = technique_df[technique_df['technique_id'] == tech_id]
    return match['technique_name'].values[0] if not match.empty else "Unknown"

def map_ids_to_names(tech_ids, technique_df):
    return [(tid, get_technique_name(tid, technique_df)) for tid in tech_ids]

# -------- Streamlit UI --------
st.set_page_config(page_title="Technique Analyzer Pro", layout="centered")
st.title("🎯 Enhanced MITRE ATT&CK TTP Predictor")

technique_id = st.text_input("Enter Technique ID", value="T1098")
threshold_percent = st.slider("Select Accuracy Threshold (%)", 0, 100, 80)

if st.button("Analyze"):
    try:
        technique_name = get_technique_name(technique_id, technique_df)

        groups = find_groups_using_technique(technique_id, group_df)
        all_related_techniques = get_all_techniques_by_groups(groups, group_df)
        filtered_techniques = filter_techniques_by_accuracy(all_related_techniques, groups, group_df, threshold_percent)

        st.markdown(f"### 🔍 Technique Selected: **{technique_id} - {technique_name}**")

        st.subheader("👥 Groups Using This Technique")
        st.write(groups if groups else "No matching groups found.")

        st.subheader("🧩 All Techniques Used By These Groups")
        all_related_named = map_ids_to_names(set(all_related_techniques), technique_df)
        st.dataframe(pd.DataFrame(all_related_named, columns=["Technique ID", "Technique Name"]))

        st.subheader(f"✅ Techniques Used by ≥ {threshold_percent}% of These Groups")
        if filtered_techniques:
            filtered_named = map_ids_to_names(filtered_techniques, technique_df)
            st.dataframe(pd.DataFrame(filtered_named, columns=["Technique ID", "Technique Name"]))
        else:
            st.warning("No techniques met the accuracy threshold.")

    except Exception as e:
        st.error(f"Error during analysis: {e}")
