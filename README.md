
# swissknife

This is my first project over 100 lines and the first web application.  I work for a small provider. We're using vlan per custome IPoE sheme client.  This application is designed to facilitate the work of our Department. At the moment it is not intended for use in another network. We have a billing in which the possibility of adding to the map devices and links between them.
![enter image description here](https://github.com/borgkun/swissknife/blob/master/demo.png?raw=true)

This utility retrieves device data from billing and builds a graph. 
At the moment, several functions are implemented:
	
 - Finding shortest path between device A and B with ports. The application wors with rings and difficult topologi.
 - Writing trunk vlan to the necessary ports.
 - Writing Access port
 - Supported Raisecom, Dlink switches. Some function supported for cisco routers, ubiquity devices
 - Template generator. Based on jinja2 template engine.

### Youtube demo
<a href="http://www.youtube.com/watch?feature=player_embedded&v=a54-OsptvU0
" target="_blank"><img src="http://img.youtube.com/vi/a54-OsptvU0/0.jpg" 
alt="IMAGE ALT TEXT HERE" width="240" height="180" border="10" /></a>
