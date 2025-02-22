from django.shortcuts import render, HttpResponse, redirect
import requests
from django.http import JsonResponse
from .models import City
from django.contrib import messages
# Create your views here.

def home(request):
    api_key = "0e9b3f7bea91fc03f5bd05877cfa488b"
    url = "https://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid={}"

    if request.method == 'POST':
        city_name = request.POST.get('city')  # get the city from the POST request  
        response = requests.get(url.format(city_name, api_key)).json()
        if  response['cod'] == 200:
            if not City.objects.filter(name=city_name).exists():  
              # save the city
              City.objects.create(name=city_name)
              messages.success(request, f'City {city_name} added successfully!')
            else:
                messages.info(request, f'City {city_name} already exists!')
        else:
            messages.error(request, f'City {city_name} not fount!')
        return redirect('home')
    weather_data = []
    # Fetch weather data for all if not match
    try:
        cities = City.objects.all().order_by('-id')
        for city in cities:
            response = requests.get(url.format(city.name, api_key))    
            data =  response.json()
            if data['cod'] == 200:
                city_weather = {
                    'city': city.name,
                    'temperature': data['main']['temp'],
                    'description': data['weather'][0]['description'],
                    'icon': data['weather'][0]['icon'],
                }
                weather_data.append(city_weather)
            else:
                City.objects.filter(name=city.name).delete()
    except requests.RequestException as e:
        print("Error", e)
    context = {"weather_data": weather_data}
    return render(request, 'index.html', context)

