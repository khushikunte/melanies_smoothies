import streamlit as st
from snowflake.snowpark.functions import col
import requests

st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# Input for name on order
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be: ', name_on_order)

# Connect to Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# Fetch fruit options
my_dataframe = session.table("smoothies.public.fruit_options").select(col('fruit_name'), col('search_on'))
pd_df = my_dataframe.to_pandas()
st.dataframe(pd_df)

# Multiselect for ingredients
ingredients_list = st.multiselect(
    'Choose up to 5 Ingredients:',
    options=pd_df['fruit_name'].tolist(),
    max_selections=5
)

if ingredients_list:
    # Nutrition information and order string
    ingredients_string = ''.join(sorted(ingredients_list))

    for fruit_chosen in ingredients_list:
        search_on = pd_df.loc[pd_df['fruit_name'] == fruit_chosen, 'search_on'].iloc[0]
        st.subheader(f"{fruit_chosen} Nutrition Information")

        try:
            response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")
            response.raise_for_status()
            sf_data = response.json()
            st.dataframe(data=sf_data, use_container_width=True)
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching data for {fruit_chosen}: {e}")

    # Prepare insert statement
    time_to_insert = st.button('Submit Order')
    if time_to_insert:
        try:
            session.sql(
                """
                INSERT INTO smoothies.public.orders (ingredients, name_on_order)
                VALUES (:ingredients, :name)
                """,
                {
                    "ingredients": ingredients_string,
                    "name": name_on_order
                }
            ).collect()
            st.success(f"✅ Your Smoothie is ordered, {name_on_order}!")
        except Exception as e:
            st.error(f"Error submitting order: {e}")
