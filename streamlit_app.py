# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import dsa
from cryptography.hazmat.primitives import serialization

# Write directly to the app
st.title(":cup_with_straw: Customize your Smoothie! :cup_with_straw:")
st.write(
  """Choose the fruits you want in your custom Smootihe"""
)

name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your smoothie will be: ', name_on_order)

with open("/Users/vladanstrbac/ssl/rsa_key.p8", "rb") as key:
    p_key = serialization.load_pem_private_key(
        key.read(),
        password=os.environ["PRIVATE_KEY_PASSPHRASE"].encode(),
        backend=default_backend(),
    )

pkb = p_key.private_bytes(
    encoding=serialization.Encoding.DER,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption(),
)

cnx = st.connection("snowflake", type="snowflake", private_key=pkb)

session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
#st.dataframe(data=my_dataframe, use_container_width=True)
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients',
    my_dataframe,
    max_selections = 5
)
if ingredients_list:
    st.write(ingredients_list)
    st.text(ingredients_list)
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' ' 

    st.write(ingredients_string)

    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
            values ('""" + ingredients_string + """', '""" + name_on_order + """')"""

    st.write(my_insert_stmt)

    time_to_insert = st.button('Submit Order')
    if time_to_insert:
        session.sql(my_insert_stmt).collect()

        st.success('Your smootie is ordered',)
