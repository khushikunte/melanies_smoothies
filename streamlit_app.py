import streamlit as st
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col
import re  # Regular expression module

# App title and description
st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

name_on_order = st.text_input('Name on Smoothie:')
cleaned_name = re.sub(r'["\']', '', name_on_order.strip())  # Remove quotes and spaces

st.write(f'The cleaned name on your Smoothie will be: {cleaned_name}')

# Proceed with the smoothie creation process
cnx = st.connection("snowflake")
session = cnx.session()

# Get fruit options from Snowflake
my_dataframe = session.table("smoothies.public.fruit_options").select(col('fruit_name'), col('search_on'))
st.dataframe(data=my_dataframe, use_container_width=True)

# Convert dataframe to pandas for further processing
pd_df = my_dataframe.to_pandas()
st.dataframe(pd_df)

# Ingredients selection
ingredients_list = st.multiselect('Choose up to 5 Ingredients:', my_dataframe, max_selections=5)

if ingredients_list:
    ingredients_string = ''
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

        # Fetch nutrition information (handle exceptions)
        search_on = pd_df.loc[pd_df['fruit_name'] == fruit_chosen, 'search_on'].iloc[0]
        st.subheader(f'{fruit_chosen} Nutrition Information')
        
        # This part can be replaced with your API call to fetch nutrition info
        # Assuming a valid API or response is being returned
        st.write(f"Nutrition data for {fruit_chosen} would be here.")  # For testing

    # Build the insert statement for Snowflake
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{cleaned_name}')
    """

    time_to_insert = st.button('Submit Order')
    
    if time_to_insert:
        try:
            session.sql(my_insert_stmt).collect()
            st.success(f"✅ Your Smoothie is ordered, {cleaned_name}!")
        except Exception as e:
            st.error(f"Something went wrong: {e}")
