import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# --------------------
# Page Configuration
# --------------------
st.set_page_config(page_title="Cultural Connect", layout="wide")

# --------------------
# Load Data with Caching
# --------------------
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("cultural_data.csv")
        return df.fillna("")  # Avoid NaNs in UI
    except FileNotFoundError:
        st.error("Data file not found. Please upload 'cultural_data.csv'.")
        return pd.DataFrame()

data = load_data()

# --------------------
# Sidebar Navigation
# --------------------
if not data.empty:
    menu = st.sidebar.radio("Navigate", ["Home", "Art Forms", "Experiences", "Responsible Tourism", "Plan Your Journey"])

    # --------------------
    # Home Page
    # --------------------
    if menu == "Home":
        st.title("🇮🇳 Cultural Connect")
        st.markdown("""
        Welcome to **Cultural Connect**, a platform to explore India's diverse traditional art forms, experience cultural richness, and practice responsible tourism.
        """)

    # --------------------
    # Art Forms Section
    elif menu == "Art Forms":
        st.header("🎨 Traditional Art Forms")
        art_data = data[data["Category"] == "ArtForm"]

        selected_regions = st.multiselect("Select Regions", art_data["Region"].unique())

        if selected_regions:
            filtered = art_data[art_data["Region"].isin(selected_regions)]
            if filtered.empty:
                st.info("No art forms found for the selected regions.")
            else:
                for _, row in filtered.iterrows():
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        if row["ImageURL"]:
                            st.image(row["ImageURL"], width=300)
                        else:
                            st.markdown("*Image not available*")
                    with col2:
                        st.subheader(row.get("ArtForm", "Unknown Art Form"))
                        st.write(row.get("Description", "No description available."))
                        st.markdown(f"**Origin:** {row.get('Origin', 'Unknown')}")
                        st.markdown(f"**Type:** {row.get('Type', 'Unspecified')}")

    # --------------------
    # Experiences Section
    elif menu == "Experiences":
        st.header("🌍 Cultural Experiences")
        exp_data = data[data["Category"] == "Experience"]

        if not exp_data.empty:
            selected_region = st.selectbox("Choose a Region", exp_data["Region"].unique())
            filtered_exp = exp_data[exp_data["Region"] == selected_region]

            search_query = st.text_input("Search for an experience...")
            if search_query:
                filtered_exp = filtered_exp[filtered_exp["ExperienceName"].str.contains(search_query, case=False, na=False)]

            if filtered_exp.empty:
                st.info("No experiences match your search.")
            else:
                for _, row in filtered_exp.iterrows():
                    st.subheader(row.get("ExperienceName", "Unnamed Experience"))
                    if row["VideoURL"]:
                        st.video(row["VideoURL"])
                    else:
                        st.markdown("*Video not available*")
                    st.write(row.get("ExperienceDescription", "No description provided."))
        else:
            st.info("No experience data available.")

    # --------------------
    # Responsible Tourism
    elif menu == "Responsible Tourism":
        st.header("♻️ Responsible Tourism Tips")
        st.markdown("""
        - Respect local customs and dress codes  
        - Reduce plastic use and waste  
        - Support local artisans by buying authentic crafts  
        - Avoid activities that exploit animals or local communities  
        - Choose eco-friendly accommodation and transport
        """)

    # --------------------
    # Plan Your Journey
    elif menu == "Plan Your Journey":
        st.header("🧭 Plan Your Cultural Journey")
        if "Lat" in data.columns and "Lon" in data.columns:
            m = folium.Map(location=[22.9734, 78.6569], zoom_start=5)

            for _, row in data.iterrows():
                try:
                    lat, lon = float(row["Lat"]), float(row["Lon"])
                    label = row["ArtForm"] if row["Category"] == "ArtForm" else row.get("ExperienceName", "Location")
                    popup = f"{label} - {row['Region']}"
                    icon_color = "blue" if row["Category"] == "ArtForm" else "green"

                    folium.Marker(
                        location=[lat, lon],
                        popup=popup,
                        tooltip=label,
                        icon=folium.Icon(color=icon_color)
                    ).add_to(m)
                except (ValueError, KeyError):
                    continue  # Skip bad rows

            st_folium(m, width=700, height=500)
        else:
            st.warning("Location data not available in the dataset.")
else:
    st.warning("The dataset is empty or could not be loaded.")

