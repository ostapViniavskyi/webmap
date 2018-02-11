# This module generates html map that has three layers: locations, where films
# were filmed, population of countries and lakes of North America
import pandas as pd
import folium
import geopy
from math import nan


def read_films_by_year(path, year):
    """
    (str, int) -> pandas.DataFrame
    Read films from file that were filmed in particular year and store their
    name and filming location in tha pandas DataFrame
    """
    films = {'name': [], 'location': []}
    with open(path, 'r', encoding='utf-8', errors='ignore') as filecontent:
        for line in filecontent:
            if line == '==============\n':
                break
        for line in filecontent:
            if '(' + str(year) + ')' in line or '(' + str(year) + '/' in line:
                films['name'].append(line.strip().split('\t')[0])
                location = line.strip().split('\t')[-2].strip() \
                    if line.strip().split('\t')[-1][0] == '(' \
                    else line.strip().split('\t')[-1].strip()
                films['location'].append(location)
    films = pd.DataFrame(films)
    return films


def read_locations(path):
    """
    (str, int) -> dict(str: tuple)
    Read latitude and longitude of all locations, where films where filmed from
    file and store them in the dictionary where names of locations are keys
    and tuple of coordinates as values
    """
    locations = {}
    with open(path, 'r', encoding='utf-8', errors='ignore') as filecontent:
        filecontent.readline()
        for line in filecontent:
            spline = line.strip().split('\t')
            if len(spline) < 3:
                continue
            locations[spline[0]] = (float(spline[1]), float(spline[2]))
    return locations


def find_coordinates(locations, df):
    """
    dict(str: tuple), pd.DataFrame -> pd.DataFrame
    Return dataframe where location column is replaced by corresponding
    coordinates columns
    """
    df['latitude'] = df.apply(lambda x:
                              locations.get(x.location,(nan, nan))[0], axis=1)
    df['longitude'] = df.apply(lambda x:
                               locations.get(x.location,(nan, nan))[1], axis=1)
    del df['location']
    return df


def create_map(df, markers_num=100):
    """
    (pd.DataFrame, int) -> None
    Create map with 3 layers: films locations, country population and
    lakes in North America. markers_num parameter shows how many markers will
    be displayed on the map, if that number is available.
    """
    map = folium.Map()

    # add films markers to the map
    fg1 = folium.FeatureGroup(name='Films')
    df = pd.DataFrame(df.groupby(['longitude', 'latitude']).
                      apply(lambda x: '</li><li>'.join(x['name'])),
                      columns=['name'])
    df['name'] = '<ul><li>' + df['name'] + '</li></ul>'
    df.reset_index(inplace=True)
    df = df.sample(frac=1).reset_index(drop=True)
    for index, x in df.iterrows():
        if index < markers_num:
            i_frame = folium.IFrame(html=x['name'], width=700, height=200)
            name = folium.Popup(i_frame, parse_html=True)
            fg1.add_child(folium.Marker(location=[x['latitude'],
                                                  x['longitude']],
                                        popup=name, icon=folium.Icon()))
        else:
            break
    map.add_child(fg1)

    # add population data to the map
    pop = folium.FeatureGroup(name='Population')
    pop.add_child(folium.GeoJson(data=open('world.json', 'r',
                                 encoding='utf-8-sig').read(),
                                 style_function=lambda x: {'fillColor': 'green'
           if x['properties']['POP2005'] < 10000000
           else 'orange' if 10000000 <= x['properties']['POP2005'] < 50000000
           else 'red'}))
    map.add_child(pop)

    # add lakes of North America on the map
    lakes = folium.FeatureGroup(name='Lakes NA')
    lakes.add_child(folium.GeoJson(data=open('lakes_na.geojson', 'r',
                                             encoding='utf-8-sig').read()))
    map.add_child(lakes)

    map.add_child(folium.LayerControl())
    map.save('films_map.html')
    print('Map is ready to use!!!')


def main():
    try:
        year = int(input('Year: '))
        marker_num = int(input('Markers number: '))
        if year < 0 or marker_num < 0:
            raise ValueError('Year and markers number must be \
                             positive integers')
        # read films from particular year into films dataframe
        films = read_films_by_year('locations.list', year)
        # read coordinates of locations form tsv file
        locations = read_locations('locations.tsv')
        # update films dataframe with coordinates of locations
        films = find_coordinates(locations, films)
        # drop missing values
        films.dropna(how='any', inplace=True)

        create_map(films, marker_num)

    except ValueError as err_message:
        print(err_message)


main()
