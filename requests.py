from urllib.parse import urlencode
from urllib.request import Request, urlopen

url = 'http://10.10.0.255:5000/raspi' # Set destination URL here

def send_image_to_server(base64, extension):
  post_fields = {'image': base64, 'extension': extension} 
  
  request = Request(url, urlencode(post_fields).encode())
  json = urlopen(request).read().decode()
  
  return json
  