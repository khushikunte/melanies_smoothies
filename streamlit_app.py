# Import required packages
import streamlit as st
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col, when_matched

# App title and description
st.title(":cup_with_straw: Pending Smoothie Orders :cup_with_straw:")
st.write("Orders that need to be filled.")

# Snowflake session
session = get_active_session()

# Fetch pending orders
orders_of = session.table("SMOOTHIES.PUBLIC.ORDERS")
pending_orders_df = orders_of.filter(col("ORDER_FILLED") == 0).to_pandas()

if not pending_orders_df.empty:
    # Display data editor for pending orders
    editable_df = st.data_editor(pending_orders_df)

    # Button to submit changes
    submitted = st.button('Submit')

    if submitted:
        # Convert edited DataFrame to Snowflake DataFrame
        edited_dataset = session.create_dataframe(editable_df)

        # Debug: Show edited data
        st.write("Edited DataFrame:", editable_df)

        # Perform merge operation
        try:
            og_dataset = session.table("SMOOTHIES.PUBLIC.ORDERS")
            og_dataset.merge(
                edited_dataset,
                (og_dataset["ORDER_UID"] == edited_dataset["ORDER_UID"]),
                [when_matched().update({"ORDER_FILLED": edited_dataset["ORDER_FILLED"]})],
            )

            st.success('Order(s) Updated!', icon='👍')
        except Exception as e:
            st.error(f"Something went wrong: {e}")
else:
    st.info('There are NO PENDING ORDERS RIGHT NOW', icon='✅')
