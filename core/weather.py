import requests
import dotenv
import geocoder
import os
dotenv.load_dotenv()

class weather:
    def __init__(self,city) :
        self.city = city
    def weather(self):
        api_key = os.getenv("weather_api")
        base_url = 'https://api.openweathermap.org/data/2.5/weather?'
        url = base_url+'appid='+api_key+'&q='+self.city+'&units=metric'
        response = requests.get(url)
        x=response.json()
        if x['cod']!=401:
            city_name = x['name']
            weather_desc = x['weather'][0]['main']
            temp = x['main']['temp']
            temp_min = x['main']['temp_min']
            temp_max = x['main']['temp_max']
            
            report = f"Weather in {city_name}: {weather_desc}, Temperature: {temp}°C, Min: {temp_min}°C, Max: {temp_max}°C"
            return report
        else:
            return "City not found"

def tellmeTodaysWeather():
    g = geocoder.ip('me')
    city = g.city
    obj = weather(city)
    return obj.weather()

if __name__ == "__main__":
    print(tellmeTodaysWeather())
