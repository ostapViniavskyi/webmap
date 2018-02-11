# webmap
HTML map of locations, where films were filmed
Module that generates map with 3 layers:
  - based on year finds and marks on map given number of locations, where films in that year were filmed.
    If more then one film was filmed on some location, all films filmed there will be listed.
    User can control, how many markers they would like to see. If number of markers specified by user is bigger than available
    number of markers for that year, all markers will be displayed.  
    Films filmed in particular year are loaded from <b>location.list</b> file.  
    All unique locations along with their coordinates are loaded from <b>locations.tsv</b> file. All coordinates
    from <b>locations.tsv</b> are got using <i>geopy</i> module.
    
  ![alt text](https://github.com/ostapViniavskyi/webmap/blob/master/examples/map_films_layer.png)
  
  - second layer colores contries on the map in 3 different colors(green, yellow and red) based on the data from <b>world.json</b> file.
  
  ![alt text](https://github.com/ostapViniavskyi/webmap/blob/master/examples/map_population_layer.png)
  
  - third layer marks on the map lakes in North America region based on the data from <b>lakes_na.geojson</b> file.
  
  ![alt text](https://github.com/ostapViniavskyi/webmap/blob/master/examples/map_na_lakes_layer.png)
  
User can control which layers to display.  
In <b>films_map.html</b> is example for 1895 years with 8 unique locaiton.
