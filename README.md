# HowFarCanIGo

![Map of London showing how far I can travel from my home in Ealing for set cut-off times](https://raw.githubusercontent.com/SebStrug/HowFarCanIGo/map_London.jpg)

Create a personalised map showing how far you can go for set distances of time using the Google API

To use:
1. Set up a Google API key and store it in a text file labelled 'api_key.txt', or just paste it into your code directly
2. Put your home/origin address as a string in a text file labelled 'home_address.txt'
    You can also put your latitude and longitude in the line below, separated by a comma, to minimise Google API calls.
(3.) Define your maximum and minimum latitudes and longitudes if using the global version of the map
4. Define whether you want to see walking or transit (public transport data)
5. Choose whether you want a local map (branching outwards from your origin), or a global map (looking at points across a space defined by your maximum and minimum coordinates).
6. Define how many points you want to query. Start from a small number e.g. 10, as a lattice is formed of N squared points.
    Not been tested for > 200 points.
7. Define your cutoff times in minutes as a list
(8.) Define a custom cmap if so interested.

Enjoy!
