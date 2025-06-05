import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

# -------- SETTINGS --------
DATA_FOLDER = r"..\data\groups"  # Pas dit pad aan naar jouw folder

# -------- LOAD DATA --------
@st.cache_data
def load_data(data_folder):
    csv_files = [f for f in os.listdir(data_folder) if f.endswith(".csv")]
    df_list = []
    for f in csv_files:
        group_name = os.path.splitext(f)[0]
        df_tmp = pd.read_csv(os.path.join(data_folder, f))
        df_tmp['group'] = group_name
        df_list.append(df_tmp)
    df = pd.concat(df_list, ignore_index=True)
    
    # Probeer birthdate om te zetten naar leeftijd
    if 'birthdate' in df.columns:
        df['birthdate'] = pd.to_datetime(df['birthdate'], errors='coerce')
        df['age'] = (pd.to_datetime('today') - df['birthdate']).dt.days // 365

    return df

df = load_data(DATA_FOLDER)

# -------- UI --------
st.title("📊 Groepen Analyse Dashboard")

# Groepselectie
groups = df['group'].unique()
selected_group = st.selectbox("Selecteer een groep:", sorted(groups))

# Filter op geselecteerde groep
df_group = df[df['group'] == selected_group]

st.markdown(f"### 🧾 Eerste rijen van groep: `{selected_group}`")
st.dataframe(df_group)

# -------- PLOTS --------
st.markdown("### 📈 Distributies")

# Geslacht
if 'sex' in df_group.columns:
    fig1, ax1 = plt.subplots()
    sns.countplot(data=df_group, x='sex', ax=ax1)
    ax1.set_title("Verdeling Geslacht")
    st.pyplot(fig1)

# Leeftijd (indien aanwezig)
if 'age' in df_group.columns:
    fig2, ax2 = plt.subplots()
    sns.histplot(df_group['age'].dropna(), bins=20, kde=True, ax=ax2)
    ax2.set_title("Leeftijdsverdeling")
    st.pyplot(fig2)

# Andere categorische kolommen
categorical_cols = df_group.select_dtypes(include='object').columns
extra_cats = [col for col in categorical_cols if col not in ['sex', 'group']]

selected_cat = st.selectbox("📊 Kies een extra categorische kolom om te visualiseren:", extra_cats)

if selected_cat:
    fig3, ax3 = plt.subplots()
    sns.countplot(data=df_group, y=selected_cat, order=df_group[selected_cat].value_counts().index, ax=ax3)
    ax3.set_title(f"Verdeling van {selected_cat}")
    st.pyplot(fig3)

# -------- FOOTER --------
st.markdown("---")
st.markdown("🛠️ Gemaakt met Streamlit | Gebruik `streamlit run eda_dashboard.py` om dit dashboard te starten.")
