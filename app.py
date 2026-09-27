import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

df=pd.read_csv('startup_funding.csv')

#Load Data
df=pd.read_csv('startup_funding.csv')

#Drop Columns
df.drop(columns=['Sr No','Remarks'],inplace=True)

#Rename Columns
df.rename(columns=
          {'Date dd/mm/yyyy':'date',
           'Startup Name':'startup',
           'Industry Vertical':'vertical',
           'SubVertical':'subvertical',
           'City  Location':'city',
           'Investors Name':'investor',
           'InvestmentnType':'round',
           'Amount in USD':'amount'
           },inplace=True)

#date cleaning
df['date']=pd.to_datetime(df['date'],format="%d/%m/%Y",errors='coerce')
df['year']=df['date'].dt.year
df['month']=df['date'].dt.month

print(df.head())
#Amount cleaning
df['amount']=df['amount'].astype(str).str.replace(',','')

df['amount']=pd.to_numeric(df['amount'],errors='coerce')

#Investor cleaning
df['investor'] = (
    df['investor']
    .astype(str)
    .str.lower()
    .str.replace(r'\(.*?\)', '', regex=True)
    .str.replace(r'[^a-z0-9\s]', '', regex=True)
    .str.replace(r'\s+', ' ', regex=True)
    .str.strip()
)
df['investor'] = df['investor'].replace(
        {'undisclosed investors': 'undisclosed', 'undisclosed investor': 'undisclosed'})
#Startup Cleaning
df['startup'] = (
    df['startup']
    .astype(str)
    .str.lower()
    .str.replace(r'xe2x80x99', '', regex=True)
    .str.replace(r'[^a-z0-9\s]', '', regex=True)
    .str.replace(r'\s+', ' ', regex=True)
    .str.strip()
)

#Create unique lists for all
startup_list=sorted(df['startup'].dropna().unique().tolist())
investor_list=sorted(df['investor'].dropna().unique().tolist())

#Create sidebar
st.sidebar.title('Indian Startup Funding Analysis')
option=st.sidebar.selectbox(
    'Select One',
    ['Overall Analysis','Startup','Investor']
)

#Overall Analysis
if option=='Overall Analysis':
    st.title('Overall Startup Funding Analysis')

    #cards
    total=round(df['amount'].sum(),2)
    max_funding=round(df.groupby('startup')['amount'].sum().sort_values(ascending=False).values[0],2)
    avg_funding=round(df.groupby('startup')['amount'].sum().mean(),2)
    total_startups=df['startup'].nunique()
    col1,col2,col3,col4=st.columns(4)
    col1.metric('Total Funding',f'${total:,}')
    col2.metric('Max Funding',f'${max_funding:,}')
    col3.metric('Avg Funding',f'${avg_funding:,}')
    col4.metric('Total Startups',total_startups)

    #MOM Chart
    st.subheader('Month on Month Funding Count')
    temp=df.groupby(['year','month'])['startup'].count().reset_index()
    temp['x']=temp['month'].astype(str)+"-"+temp['year'].astype(str)

    fig=px.line(temp,
                x='x',
                y='startup')
    st.plotly_chart(fig,use_container_width=True)

    #Sector Analysis
    st.subheader('Top Sectors')
    sector=df.groupby('vertical')['amount'].sum().sort_values(ascending=False).head(10)
    fig=px.pie(
        values=sector.values,
        names=sector.index
    )
    st.plotly_chart(fig,use_container_width=True)

    #Funding Type
    st.subheader('Funding Type')
    funding_type=df['round'].value_counts()
    fig=px.bar(x=funding_type.index,
               y=funding_type.values)
    st.plotly_chart(fig,use_container_width=True)

#City wise funding
    st.subheader('City Wise Funding')
    city=df.groupby('city')['amount'].sum().sort_values(ascending=False).head(10)
    fig=px.bar(x=city.index,y=city.values)
    st.plotly_chart(fig,use_container_width=True)

    #Top StartUps
    st.subheader('Top Startups')
    top_startups=(
        df.groupby('startup')['amount'].sum().sort_values(ascending=False).head(10)
    )
    st.dataframe(top_startups)

    #Top Investors
    st.subheader('Top Investors')
    top_investors=df['investor'].value_counts().head(10)
    st.dataframe(top_investors)

    #Heatmap
    st.subheader('Funding Heatmap')
    heatmap=df.pivot_table(
        index='city',
        columns='year',
        values='amount',
        aggfunc='sum'
    )
    st.dataframe(heatmap)

elif option=='Startup':
    selected_startup=st.sidebar.selectbox(
        'Select Startup',
        startup_list
    )
    st.title(selected_startup.upper())
    startup_df=df[df['startup']==selected_startup]

    #Basic details
    st.subheader('Basic Details')
    st.write('Industry:',startup_df['vertical'].iloc[0])
    st.write('SubIndustry:',startup_df['subvertical'].iloc[0])
    st.write('Location:',startup_df['city'].iloc[0])
#Funding Rounds
    st.subheader('Funding Rounds')
    st.dataframe(startup_df[['date','round','investor','amount']])

    #Total Funding
    st.subheader('Total Funding')
    st.metric('Funding Raised',f'${round(startup_df['amount'].sum()):,}')

    #Similar startups
    st.subheader('Similar Startups')
    similar=df[df['vertical']==startup_df['vertical'].iloc[0]]['startup'].unique()
    st.write(similar)

elif option=='Investor':
    selected_investor=st.sidebar.selectbox(
        'Select Investor',
        investor_list
    )
    st.title(selected_investor.upper())
    investor_df=df[df['investor']==selected_investor]

    #Recent Investments
    st.subheader('Recent Investments')
    recent=investor_df.sort_values(by='date',ascending=False)[['date','startup','vertical','city','amount']]
    st.dataframe(recent)

    #Biggest Investments
    st.subheader('Biggest Investments')
    biggest=investor_df.sort_values(by='amount',ascending=False)[['startup','amount']].head(10)
    st.dataframe(biggest)

    #General Investment In
    st.subheader('Generally Invested IN')
    st.write(investor_df['vertical'].mode()[0])

    #Sector Pie
    st.subheader('Sector Distribution')
    sector=investor_df['vertical'].value_counts().head(10)
    fig=px.pie(
        values=sector.values,
        names=sector.index
    )
    st.plotly_chart(fig,use_container_width=True)

#Stage Pie
    st.subheader('Funding Stage')
    stage=investor_df['round'].value_counts()
    fig=px.pie(
        values=stage.values,
        names=stage.index
    )
    st.plotly_chart(fig,use_container_width=True)

    #City Pie
    st.subheader('City Distribution')
    city = investor_df['city'].value_counts()
    fig = px.pie(
        values=city.values,
        names=city.index
    )
    st.plotly_chart(fig, use_container_width=True)

    #YOY Graph
    st.subheader('YOY investments')
    yoy=investor_df.groupby('year')['amount'].sum().reset_index()

    fig=px.line(
        yoy,
        x='year',
        y='amount'
    )
    st.plotly_chart(fig,use_container_width=True)

    #Similar Investors
    st.subheader('Similar Investor')
    similar=df[df['vertical'].isin(investor_df['vertical'].unique())]['investor'].value_counts().head(10)
    st.write(similar)
