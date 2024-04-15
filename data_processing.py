import pandas as pd
import plotly.express as px
import folium
from branca.colormap import LinearColormap
from folium import plugins
import numpy as np

def load_data():
    powerlifting_data = pd.read_csv("power.csv")
    data_capitale = pd.read_csv("capitale.csv")

    mapping = {
    'USSR': 'Russia',
    'Czechia': 'Czech Republic',
    'Tahiti': 'French Polynesia',
    'UAE' : 'United Arab Emirates',
    'England' : 'United Kingdom',
    'USA' : 'United States',
    'UK' : 'United Kingdom',
    'Scotland' : 'United Kingdom',
    'Wales' :'United Kingdom',
    'N.Ireland' : 'Ireland',
    'West Germany' : 'Germany',
    'Congo' : 'Republic of Congo',
    'North Macedonia' : 'Macedonia'
}
    mapping_capitales = {
        "Cote d'Ivoire":'Ivory Coast'
}

    powerlifting_data['Country'] = powerlifting_data['Country'].replace(mapping)
    data_capitale['CountryName'] = data_capitale['CountryName'].replace(mapping_capitales)

    powerlifting_data_cleaned = powerlifting_data.dropna(subset=['TotalKg']).query('Equipment == "Raw"').query('Date > "2000-01-01"').drop(columns=['BirthYearClass', 'Division', 'WeightClassKg', 'State'])

    # Assign weight categories based on sex and body weight using nested np.where
    powerlifting_data_cleaned['WeightCategory'] = np.where(
        powerlifting_data_cleaned['Sex'] == 'M',
        np.where(
            powerlifting_data_cleaned['BodyweightKg'] < 59, '-59kg',
            np.where(
                powerlifting_data_cleaned['BodyweightKg'] < 66, '-66kg',
                np.where(
                    powerlifting_data_cleaned['BodyweightKg'] < 74, '-74kg',
                    np.where(
                        powerlifting_data_cleaned['BodyweightKg'] < 83, '-83kg',
                        np.where(
                            powerlifting_data_cleaned['BodyweightKg'] < 93, '-93kg',
                            np.where(
                                powerlifting_data_cleaned['BodyweightKg'] < 105, '-105kg',
                                np.where(
                                    powerlifting_data_cleaned['BodyweightKg'] < 120, '-120kg',
                                    '+120kg'
                                )
                            )
                        )
                    )
                )
            )
        ),
        np.where(
            powerlifting_data_cleaned['Sex'] == 'F',
            np.where(
                powerlifting_data_cleaned['BodyweightKg'] < 47, '-47kg',
                np.where(
                    powerlifting_data_cleaned['BodyweightKg'] < 52, '-52kg',
                    np.where(
                        powerlifting_data_cleaned['BodyweightKg'] < 57, '-57kg',
                        np.where(
                            powerlifting_data_cleaned['BodyweightKg'] < 63, '-63kg',
                            np.where(
                                powerlifting_data_cleaned['BodyweightKg'] < 69, '-69kg',
                                np.where(
                                    powerlifting_data_cleaned['BodyweightKg'] < 76, '-76kg',
                                    np.where(
                                        powerlifting_data_cleaned['BodyweightKg'] < 84, '-84kg',
                                        '+84kg'
                                    )
                                )
                            )
                        )
                    )
                )
            ),
            'Unknown'  # Default category if no conditions are met
        )
    )

    # Fusionner les données et effectuer les opérations de filtrage
    merged_data = (
        pd.merge(data_capitale, powerlifting_data_cleaned, left_on='CountryName', right_on='Country', how='inner')
        .query('CapitalLatitude != 0 and CapitalLongitude != 0')
        .groupby(['CapitalName', 'CountryName', 'CapitalLatitude', 'CapitalLongitude'])
        .agg(TotalParticipants=('TotalKg', 'count'))
        .reset_index()
    )

    # Filter for French athletes
    french_athletes = powerlifting_data_cleaned.query(
        'Event == "SBD" and Place == "1" and Age <= 23 and Sex == "M" and ParentFederation == "IPF" and Country == "France"'
    )

    # Filter for Sheffield participants
    sheffield_participants = powerlifting_data_cleaned.query(
        'MeetName == "Sheffield Powerlifting Championships"'
    )[['Name', 'Sex', 'WeightCategory', 'Age', 'BodyweightKg', 'TotalKg']]

    return powerlifting_data_cleaned, merged_data, french_athletes, sheffield_participants

def french_athlete_performance(df):
    
    # Create a scatter plot
    fig = px.scatter(
        df,
        x='Date',
        y='TotalKg',
        color='WeightCategory',
        labels={'Date': 'Date', 'TotalKg': 'Total de poids (kg)'},
        hover_data=['Name', 'Age', 'WeightCategory', 'TotalKg']
    )

    return fig

def participants_per_year(df, selected_gender):
    # Filter data based on the selected gender
    if selected_gender != 'All':
        df = df[df['Sex'] == selected_gender]
    
    # Create a bar plot
    fig = px.bar(
        df, 
        x='Year', 
        title='Nombre de participant par année',
        labels={'Year': 'Année', 'count': 'Nombre de participant'},
    )
    return fig

def age_histogram(df):
    fig = px.histogram(df, x='Age', nbins=30, title="Distribution des athlètes selon l'Age")
    fig.update_layout(xaxis_title='Age', yaxis_title='Frequece')
    return fig

def gender_pie_chart(df):
    fig = px.pie(df, names='Sex', title='Distribution des atlètes par genre')
    return fig

def weight_category_bar_chart(df, selected_gender):
    try:
        # Filter data based on the selected gender
        filtered_data = df[df['Sex'] == selected_gender]
        
        # Check if the filtered data is empty
        if filtered_data.empty:
            print("No data available for the selected gender.")
            return px.bar(title="No data available for the selected gender")
        
        # Group by weight category and count the number of athletes
        weight_category_distribution = filtered_data.groupby('WeightCategory').size().reset_index(name='count')

        # Check if the grouped data is empty
        if weight_category_distribution.empty:
            print("No data available after grouping by weight category.")
            return px.bar(title="No data available after grouping by weight category")

        sorted_categories = sorted(weight_category_distribution['WeightCategory'].unique())
        weight_category_distribution = weight_category_distribution.set_index('WeightCategory').reindex(sorted_categories).reset_index()

        # Create a bar plot
        fig = px.bar(
            weight_category_distribution,
            x='WeightCategory',
            y='count',
            title=f'Distribution des athlètes {selected_gender} selon leurs catégories de poids',
            labels={'WeightCategory': 'Catégorie de poids', 'count': "Nombre d'athlètes"}
        )

        return fig
    except Exception as e:
        print("An error occurred while creating the weight category bar chart: ", e)
        return px.bar(title="An error occurred while creating the chart")
    
def best_performance_plot(data, gender, lift, year):
    # Convert 'Date' to datetime and extract 'Year'
    data['Date'] = pd.to_datetime(data['Date'])
    data['Year'] = data['Date'].dt.year
    
    # Filter data based on the selected gender, lift, and year
    filtered_data = data.query(f'Sex == "{gender}" and Year == {year}')
    
    if lift != "TotalKg":
        lift = f"Best3{lift}Kg"
        filtered_data = filtered_data.dropna(subset=[lift])
    
    # Summarize data to find the best performance per weight category
    summarized_data = filtered_data.groupby('WeightCategory').agg(BestPerformance=(lift, 'max')).reset_index()
    
    # Create the plot
    fig = px.bar(
        summarized_data,
        x='WeightCategory',
        y='BestPerformance',
        title=f'Meilleur {lift} Performance par Catégorie de Poids et Année',
        labels={'WeightCategory': 'Catégorie de Poids', 'BestPerformance': f'Meilleur {lift}'},
        color_discrete_sequence=['blue']
    )
    return fig

def meet_country_distribution(data):
    # Count the number of athletes per country
    meet_country_counts = data.groupby('MeetCountry').size().reset_index(name='AthleteCount').sort_values('AthleteCount', ascending=False)
    
    # Keep only the top 10 countries
    N = 10
    top_meet_countries = meet_country_counts.head(N).copy()
    
    # The rest goes to "Other"
    other_meet_countries = meet_country_counts.tail(-N)
    other_count = other_meet_countries['AthleteCount'].sum()
    other_row = pd.DataFrame({'MeetCountry': ['Others'], 'AthleteCount': [other_count]})
    
    # Combine top 10 countries and "Other"
    combined_meet_countries = pd.concat([top_meet_countries, other_row])
    
    # Create the bar chart
    fig = px.bar(
        combined_meet_countries,
        x='MeetCountry',
        y='AthleteCount',
        title='Distribution des athlètes par pays ',
        labels={'MeetCountry': 'Pays ', 'AthleteCount': "Nombre d'athlètes"},
        color_discrete_sequence=['blue']
    )
    fig.update_layout(xaxis_tickangle=-90)
    
    return fig

def competition_timeline(data):
    # Extract the year from the Date column
    data['Year'] = pd.to_datetime(data['Date']).dt.year
    
    # Count the number of competitions per year
    competition_counts = data.groupby('Year').size().reset_index(name='CompetitionCount')
    
    # Create the timeline chart
    fig = px.line(
        competition_counts,
        x='Year',
        y='CompetitionCount',
        title='Evolution du nombre de compétition par année',
        labels={'Year': 'Année', 'CompetitionCount': 'Nombre de Competitions'},
        color_discrete_sequence=['blue']
    )
    
    return fig

def compute_nombre_participants(df):
    return df['Name'].nunique()

def compute_max_total(df):
    max_total = df['TotalKg'].max()
    max_total_name = df[df['TotalKg'] == max_total]['Name'].iloc[0]
    return max_total_name, max_total

def compute_max_goodlift(df):
    df_sbd = df[df['Event'] == "SBD"]  # Filter for rows where Event is "SBD"
    max_goodlift = df_sbd['Goodlift'].max()
    max_goodlift_row = df_sbd[df_sbd['Goodlift'] == max_goodlift].iloc[0]
    return (max_goodlift_row['Name'], 
            max_goodlift_row['BodyweightKg'], 
            max_goodlift_row['TotalKg'])