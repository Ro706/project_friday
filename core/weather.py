import requests
import dotenv
import geocoder
import os
dotenv.load_dotenv()

class weather:
    def __init__(self,city) :
        self.city = city
    def weather(self):
        try:
            api_key = os.getenv("weather_api")
            if not api_key:
                return "Weather API key not found in environment variables."
            
            base_url = 'https://api.openweathermap.org/data/2.5/weather?'
            url = f"{base_url}appid={api_key}&q={self.city}&units=metric"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            x = response.json()
            
            if x.get('cod') == 200:
                city_name = x['name']
                weather_desc = x['weather'][0]['main']
                temp = x['main']['temp']
                temp_min = x['main']['temp_min']
                temp_max = x['main']['temp_max']
                
                report = f"Weather in {city_name}: {weather_desc}, Temperature: {temp}°C, Min: {temp_min}°C, Max: {temp_max}°C"
                return report
            else:
                return f"Error from weather service: {x.get('message', 'Unknown error')}"
        except Exception as e:
            return f"Failed to fetch weather: {e}"

def tellmeTodaysWeather():
    try:
        g = geocoder.ip('me')
        city = g.city if g.city else "London" # Fallback
        obj = weather(city)
        return obj.weather()
    except Exception as e:
        return f"Error determining location: {e}. Please check your internet connection."

if __name__ == "__main__":
    print(tellmeTodaysWeather())
