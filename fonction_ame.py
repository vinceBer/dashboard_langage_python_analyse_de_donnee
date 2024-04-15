import folium
from folium import plugins
from data_processing import load_data

def create_folium_map():
    _, merged_data, _, _ = load_data()
    
    # Coordonnées du centre de la carte
    center_coords = (48.7453229, 2.5073644)
    
    # Créer la carte Folium
    folium_map = folium.Map(location=center_coords, tiles='OpenStreetMap', zoom_start=2)
    
    # Créer un groupe de marqueurs
    marker_cluster = plugins.MarkerCluster().add_to(folium_map)
    
    # Ajouter des marqueurs au groupe de marqueurs
    for index, row in merged_data.iterrows():
        latitude = row['CapitalLatitude']
        longitude = row['CapitalLongitude']
        country_name = row['CountryName']
        total_participants = row['TotalParticipants']
        marker_color = assign_color(total_participants)
        popup_content = f"Country: {country_name}<br>Total Participants: {total_participants}"
        
        # Ajouter le marqueur avec la fenêtre contextuelle et la couleur spécifiée au groupe de marqueurs
        folium.Marker([latitude, longitude], popup=folium.Popup(popup_content, max_width=300),
                      icon=folium.Icon(color=marker_color)).add_to(marker_cluster)
    
    # Créer une légende pour la carte
    legend_html = '''
     <div style="position: fixed; 
                 bottom: 50px; left: 50px; width: 200px; height: 100px; 
                 border:2px solid grey; z-index:9999; font-size:14px;
                 background-color:white;
                 ">
      &nbsp; Pink : Participants > 30 000<br>
      &nbsp; Green: Participants > 10 000<br>
      &nbsp; Orange: Participants > 5 000<br>
      &nbsp; Red: Participants > 1 000<br>
      &nbsp; Black: Participants <= 1 000<br>
      </div>
     '''
    
    folium_map.get_root().html.add_child(folium.Element(legend_html))
    
    # Retourner le code HTML de la carte
    return folium_map.get_root().render()

def assign_color(total_participants):
    if total_participants > 30000:
        return 'pink'
    elif total_participants > 10000:
        return 'green'
    elif total_participants > 5000:
        return 'orange'
    elif total_participants > 1000:
        return 'red'
    else:
        return 'black'
