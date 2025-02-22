from django.shortcuts import render, redirect
import requests
from .models import City
from django.contrib import messages
from django.db import IntegrityError

def home(request):
    api_key = "0e9b3f7bea91fc03f5bd05877cfa488b"  # Replace with your OpenWeatherMap API key
    url = "https://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid={}"
    
    # Handle POST request (when a city is added)
    if request.method == 'POST':
        city_name = request.POST.get('city')  # Get the city name from the form
        
        # Validate city name
        if city_name:
            # Fetch weather data from OpenWeatherMap API
            response = requests.get(url.format(city_name, api_key)).json()
            
            # Check if the city was found in the API
            if response.get('cod') == 200:
                try:
                    # Try to create the city (will raise IntegrityError if it already exists)
                    City.objects.create(name=city_name)
                    messages.success(request, f'City {city_name} added successfully!')
                except IntegrityError:
                    # Handle the case where the city already exists
                    messages.info(request, f'City {city_name} already exists!')
            else:
                # Handle the case where the city was not found in the API
                messages.error(request, f'City {city_name} not found!')
        else:
            # Handle the case where no city name was provided
            messages.error(request, 'Please enter a city name.')
        
        # Redirect to the home page after processing the POST request
        return redirect('home')
    
    # Fetch weather data for all cities in the database
    weather_data = []
    cities = City.objects.all().order_by('-id')  # Get all cities, ordered by most recently added
    
    for city in cities:
        try:
            # Fetch weather data for the city from the API
            response = requests.get(url.format(city.name, api_key))
            data = response.json()
            
            # Check if the city was found in the API
            if data.get('cod') == 200:
                # Prepare weather data for the template
                city_weather = {
                    'city': city.name,
                    'temperature': data['main']['temp'],
                    'description': data['weather'][0]['description'],
                    'icon': data['weather'][0]['icon'],
                }
                weather_data.append(city_weather)
            else:
                # If the city was not found in the API, delete it from the database
                City.objects.filter(name=city.name).delete()
                messages.warning(request, f'City {city.name} was not found and has been removed.')
        except requests.RequestException as e:
            # Handle API request errors
            print("Error:", e)
            messages.error(request, f'Error fetching weather data for {city.name}.')
    
    # Prepare context for the template
    context = {"weather_data": weather_data}
    
    # Render the template with the weather data
    return render(request, 'index.html', context)

