# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write(
    """  Choose the fruits you want in your custom Smoothie !
    """
)
name_on_order = st.text_input('Name on Smoothie:')

cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('fruit_name'), col('search_on'))

# Convert to pandas dataframe for easier handling in Streamlit
pd_pf = my_dataframe.to_pandas()

# Clean up column names to remove any leading/trailing spaces
pd_pf.columns = pd_pf.columns.str.strip()

# Show the dataframe to verify
st.dataframe(pd_pf)

ingredients_list = st.multiselect(
    'Choose upto 5 Ingredients : '
    , pd_pf['fruit_name']
    , max_selections=5
)

# Check and process the selected ingredients
if ingredients_list:
    ingredients_string = ''
    
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ', '
        
        if 'search_on' in pd_pf.columns:
            # Check if the selected fruit exists in the dataframe
            if fruit_chosen in pd_pf['fruit_name'].values:
                try:
                    search_on = pd_pf.loc[pd_pf['fruit_name'] == fruit_chosen, 'search_on'].iloc[0]
                    st.subheader(f"{fruit_chosen} Nutrition Information")
                    smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")
                    st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
                except IndexError:
                    st.error(f"No matching search value found for {fruit_chosen}")
            else:
                st.error(f"{fruit_chosen} not found in the fruit options.")
        else:
            st.error("Column 'search_on' not found in the dataframe")

    # Insert order into the database
    my_insert_stmt = """ INSERT INTO smoothies.public.orders(ingredients, name_on_order)
                        VALUES ('""" + ingredients_string + """','""" + name_on_order + """')"""

    time_to_insert = st.button('Submit_order')
    
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f"✅ Your Smoothie is ordered, {name_on_order}!")
