// Credits, see post: https://asmaloney.com/2014/01/code/creating-an-interactive-map-with-leaflet-and-openstreetmap/

var map = L.map('map', {
  center: [-16.0, -56.0],
  minZoom: 2,
  zoom: 4,
})

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution:
    '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
  subdomains: ['a', 'b', 'c'],
}).addTo(map)

var myURL = jQuery('script[src$="leaf-geojson.js"]')
  .attr('src')
  .replace('leaf-geojson.js', '')

var myIcon = L.icon({
  iconUrl: myURL + 'images/pin24.png',
  iconRetinaUrl: myURL + 'images/pin48.png',
  iconSize: [29, 24],
  iconAnchor: [9, 21],
  popupAnchor: [0, -14],
})

L.geoJSON(geojsonFeature).addTo(map);

// for (var i = 0; i < markers.length; ++i) {
//   L.marker([markers[i].lat, markers[i].lng], { icon: myIcon })
//     .bindPopup(
//       '<a href="' +
//         markers[i].url +
//         '" target="_blank">' +
//         markers[i].name +
//         '</a>'
//     )
//     .addTo(map)
// }
