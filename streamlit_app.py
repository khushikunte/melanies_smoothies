import streamlit as st
from snowflake.snowpark.functions import col
import requests

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

name_on_order = st.text_input('Name on Smoothie:')

cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('fruit_name'), col('search_on'))
st.dataframe(data=my_dataframe, use_container_width=True)

pd_pf = my_dataframe.to_pandas()
st.dataframe(pd_pf)

ingredients_list = st.multiselect(
    'Choose up to 5 Ingredients:',
    my_dataframe['fruit_name'].tolist(),
    max_selections=5
)

if ingredients_list:
    ingredients_string = ''
    
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen
        
        try:
            search_on = pd_pf.loc[pd_pf['fruit_name'] == fruit_chosen, 'search_on'].iloc[0]
        except IndexError:
            search_on = None
            st.warning(f"Search information for {fruit_chosen} not found.")

        if search_on:
            st.subheader(f"{fruit_chosen} Nutrition Information")
            smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")
            sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
        else:
            st.warning(f"No nutrition data available for {fruit_chosen}.")
    
    # Insert into Snowflake
    my_insert_stmt = """
    INSERT INTO smoothies.public.orders (ingredients, name_on_order)
    VALUES (%s, %s)
    """
    time_to_insert = st.button('Submit Order')
    
    if time_to_insert:
        session.sql(my_insert_stmt, parameters=(ingredients_string, name_on_order)).collect()
        st.success(f"✅ Your Smoothie is ordered, {name_on_order}!")
