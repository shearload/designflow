"""
Wyeth Binder
Bollinger + Grohmann

Run Program with following command:

streamlit run corbel.py

"""
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import altair as alt
import numpy as np

# Set page title and icon
st.set_page_config(page_title="Corbel Designer", page_icon=":heart:")

# Page title and description
st.title("Corbel Design App")
st.markdown("")
st.markdown("")
st.markdown("v1.0 | Written by: Wyeth Binder | Verified by: Name, Surname")
st.markdown("")

st.markdown("This is a simple Streamlit app to design a concrete corbel.")

st.image("corbel_icon.png", caption="Corbel Diagram")

# User input - Sidebar
user_input_text = st.sidebar.text_input("Enter project name:", "VIE23 P017")
#num_new_rows = st.sidebar.number_input("Input Element Rows",8,50)
column_width = st.sidebar.number_input("Input Column Size [cm]", value=80)
pad_offset = st.sidebar.number_input("Input Pad Offset [cm]", value=5)
corbel_height = st.sidebar.slider("Corbel Height [cm]", min_value=40, max_value=120, value=65)
corbel_depth = st.sidebar.slider("Corbel depth [cm]", min_value=30, max_value=200, value=40)


st.subheader("Input RFEM data")
st.markdown("Vertical force V in kN")
st.markdown("Horizontal force H in kN")


if "df" not in st.session_state:
    placeholder_data = np.array([(150,120,"Corbel 1"),(250,65,"Corbel 2"),(200,120,"Corbel 3"),(300,50,"Corbel 4")])
    st.session_state.df = pd.DataFrame(placeholder_data, columns=["V",
                                                                    "H",
                                                                    "Location"])

# ncol = st.session_state.df.shape[1]  # col count
# rw = -1
    

st.session_state.df = st.data_editor(st.session_state.df, use_container_width=True,num_rows="dynamic")

#st.dataframe(st.session_state.df, use_container_width=True)

st.subheader("Upload RFEM data")
uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:

    # Can be used wherever a "file-like" object is accepted:
    df = pd.read_csv(uploaded_file)
    st.write(df)

length = len(st.session_state.df["H"])


# Calculation section
st.subheader("Calculation")

ac = corbel_depth/2
hc = corbel_height

if ac <= 0.2*hc:
    type = 'Extra Short Corbel'
elif ac < 0.5*hc:
    type = 'Short Corbel'
elif 0.4*hc <= ac <= hc:
    type = 'Strut and Tie Corbel'
else:
    type = 'Error: Calculate as cantilever beam if ac > hc'

st.write("Corbel calculation type = ", type)


# calculation per Schneider 20. [5.124] eqs 5.11 and 5.24
# for row in st.session_state.df:
# V = st.session_state.df["V"]
V = pd.to_numeric(st.session_state.df["V"]) #typecast to float from string or whatever streamlit has as input
# H = st.session_state.df["H"]
H = pd.to_numeric(st.session_state.df["H"])

st.write("Concrete Grade = C50/60")
st.write("Steel Grade = B500B")
fck = 50 #50Mpa = 5kN/cm2 for C50/60 concrete
fy = 500 # for B500B steel grade
fyd = 500/1.15 
Vrd = (0.5*(0.7-fck/200)*(column_width*10/2)*(corbel_height*10)*fck/1.50)/1000 #calc conc. strut with V_Rdmax = 0,5*(0,7-fck/200)*b*z*fck/gammaC (in KN)
#st.write("vrd ", Vrd)

cover = 5 #5cm concrete cover
d = corbel_height - cover
ac = corbel_depth - pad_offset #cm
z0 = d*(1-0.4*(V.divide(Vrd))) # use .divde() method on pd dataframes
#st.write("z0 ", z0)

Zed = V*(ac/z0) + H*((cover+z0)/z0) #units in cm
#st.write("zed ", Zed)

As1 = (Zed/fyd)*100 # in cm2
As2 = As1*0.5 #in cm2

# Results
st.markdown("---")
st.write("Calculated Rebar Amounts [cm2]")

run = st.button('Submit')

if run:

    column_tag = np.full((length), str(column_width) + " x " + str(column_width))
    df_results = pd.DataFrame({'Column Size':column_tag,
                               'As Anchorage': As1.round(2),
                               'As Stirrups': As2.round(2)})

    st.write(pd.concat([st.session_state.df,df_results],axis=1))

    st.write(f"Calculated Locations: {st.session_state.df.shape[0]}")
    maximum = df_results['As Anchorage'].idxmax()
    st.write(f"Max As Anchorage Location: {st.session_state.df['Location'].iloc[maximum]}")


# Footer
st.markdown("---")
st.markdown("W. Binder, 2024")

