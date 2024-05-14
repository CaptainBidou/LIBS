import streamlit as st
import numpy as np
import pandas as pd
import os
import sys
import matplotlib.pyplot as plt
sys.path.append("C:/Users/tjasr/Documents/GitHub/LIBS/LIBS_Back")
import databaseBuild

# Sidebar
cells_expanded = st.sidebar.checkbox("Expand Cells", value=True)
cells = st.sidebar.expander("Cells", expanded=cells_expanded)
cellTab = databaseBuild.getCells()
with cells:
    for cell in cellTab:
        st.write("- "+cell[1])


observers_expanded = st.sidebar.checkbox("Expand Observers", value=True)
observers = st.sidebar.expander("Observers", expanded=observers_expanded)
obsTab = databaseBuild.getObservers()
with observers:
    for observer in obsTab:
        st.write("- " + observer[1])

new_observers_expanded = st.sidebar.checkbox("Expand New Observers", value=True)
new_observers = st.sidebar.expander("New Observers", expanded=new_observers_expanded)
with new_observers:
    name = st.text_input("Name:")
    commentary = st.text_area("Commentary:")
    submit_button = st.button("Submit")

# Main Area
st.title("New Test")

# Divide the screen into two columns for "New Test" and "Parameters"
col1, col2 = st.columns(2)

with col1:
    new_test_expanded = st.checkbox("Expand New Test", value=True)
    new_test = st.expander("New Test", expanded=new_test_expanded)
    actionTab = databaseBuild.getActions()
    actionTabName = []
    for action in actionTab:
        actionTabName.append(action[1])

    with new_test:
        with new_test:
            action = st.selectbox("Action:", actionTab)
            comment = st.text_input("Comment:")
            cell_choose = st.selectbox("Cell:", cellTab)
            obsTab.append("None")
            observer_choose = st.selectbox("Observer:", obsTab)
with col2:
    parameters_expanded = st.checkbox("Expand Parameters", value=True)
    parameters = st.expander("Parameters", expanded=parameters_expanded)
    with parameters:
        current = st.slider("Current:", min_value=0, max_value=100, value=50)
        time_pulsing = st.slider("Time pulsing:", min_value=0, max_value=100, value=50)
        time_resting = st.slider("Time resting:", min_value=0, max_value=100, value=50)

# Submit button
submit_button = st.button("Start Test")

# Indicators
st.title("Indicators")

# Layout for indicators
col1_indicators, col2_indicators, col3_indicators, col4_indicators, col5_indicators, col6_indicators = st.columns(6)

with col1_indicators:
    st.write("PS-Mode:")
with col2_indicators:
    st.write("EL-Mode:")
with col3_indicators:
    st.write("EL-Status:")
with col4_indicators:
    st.write("Voltage:")
with col5_indicators:
    st.write("Current:")
with col6_indicators:
    st.write("Capacity:")

# Graphs
st.title("Graphs")

# Divide the screen into three columns for the graphs
col1_graph, col2_graph, col3_graph = st.columns(3)

# Generate some example data for plotting
time = np.arange(0, 10, 0.1)
voltage = np.sin(time)
current = np.cos(time)
capacity = np.tan(time)

with open("C:/Users/tjasr/Documents/GitHub/LIBS/LIBS_Back/datasets/BID002_CycRand_08052024.csv", 'r') as file:
    data = pd.read_csv(file, delimiter=';')
timeTab = []
voltageTab = []
currentTab = []
capacityTab = []
for i in range(len(data.values)):
    timeTab.append(i)
    voltageTab.append(data.values[i][1])
    currentTab.append(data.values[i][2])
    capacityTab.append(data.values[i][4])

chart_data = pd.DataFrame(
   {
       "col1": timeTab,
       "col2": voltageTab,
       "col3": currentTab,
       "col4": capacityTab,
   }
)

with col1_graph:
    st.write("Voltage")
    st.line_chart(chart_data[["col2"]])


with col2_graph:
    st.write("Current")
    st.line_chart(chart_data[["col3"]])

with col3_graph:
    st.write("Capacity")
    st.line_chart(chart_data[["col4"]])

#when start is pressed
if submit_button:
    st.write("Test started")
    #add the test to the database
    idTest = databaseBuild.createTest(action[0], comment, [cell_choose[0]])