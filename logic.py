import requests
from gui import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *


class Logic(QMainWindow):
    def __init__(self) -> None:

        """
   Creates the main window, sets up the GUI, and hides the weather information by default.
        """

        super().__init__()
        self.gui = Ui_WeatherWear_window()
        self.gui.setupUi(self)
        self.gui.pushButton.clicked.connect(self.getweather)
        self.hidegui()

    def hidegui(self) -> None:

        """
    Hides all information from the GUI. This is for when there is
        no data to display
        or
        if there is data that is unable to be displayed.
        """

        self.gui.city.hide()
        self.gui.state.hide()
        self.gui.dateandtime.hide()
        self.gui.temperature.hide()
        self.gui.condition.hide()
        self.gui.conditionicon.hide()
        self.gui.windspeed.hide()
        self.gui.winddirection.hide()
        self.gui.uv.hide()
        self.gui.maxtemp.hide()
        self.gui.mintemp.hide()
        self.gui.chanceofrain.hide()
        self.gui.whattowear.hide()
        self.gui.whattowhear_label.hide()

    def showgui(self) -> None:

        """
    Shows all of the ui elements on the GUI. This is used after the data is fetched and is ready to display.
        """

        self.gui.city.show()
        self.gui.state.show()
        self.gui.dateandtime.show()
        self.gui.temperature.show()
        self.gui.condition.show()
        self.gui.conditionicon.show()
        self.gui.windspeed.show()
        self.gui.winddirection.show()
        self.gui.uv.show()
        self.gui.maxtemp.show()
        self.gui.mintemp.show()
        self.gui.chanceofrain.show()
        self.gui.whattowear.show()
        self.gui.whattowhear_label.show()



    def getweather(self) -> None:

        """
    Gets weather information from the API based on the user's input,
    checks the city and state inputs 
    and gets weather data if it is valid.
        """

        state = self.gui.region_lineEdit.text().strip().title()
        city = self.gui.city_lineEdit.text().strip().title()

        if not city or not state:
            self.gui.errors.setText("City and state/region cannot be empty.")
            self.hidegui()
            return

        location_query = f"{city}, {state}"
        api_key = "306cb57db31845ea8a651324241512"
        url = "http://api.weatherapi.com/v1/forecast.json"
        parameters = {
            "key": api_key,
            "q": location_query,
            "days": 1,
            "aqi": "no"
        }

        try:
            response = requests.get(url, params=parameters)
            response.raise_for_status()
            weather_data = response.json()

            location_country = weather_data.get("location", {}).get("country", "Unknown")
            if location_country == "Unknown":
                self.gui.errors.setText("Unable to determine the location.")
                self.hidegui()
                return

            self.updategui(weather_data)
            self.showgui()
        except:
            self.gui.errors.setText("Error with processing the weather data.")
            self.hidegui()

    def updategui(self, weather_data) -> None:

        """
    Updates the GUI with weather data from the API. Shows the data for city, state, weather conditions, and suggestions.
        """

        try:
            location = weather_data.get("location", {})
            current = weather_data.get("current", {})
            forecast_data = weather_data.get("forecast", {})
            forecast_day = forecast_data.get("forecastday", [{}])
            forecast = forecast_day[0].get("day", {})
            city_name = location.get("name", "Unknown")
            region_name = location.get("region", "Unknown")
            country = location.get("country", "Unknown")
            date_time = location.get("localtime", "N/A")
            temperature = current.get("temp_f", "N/A")
            condition_data = current.get("condition", {})
            condition = condition_data.get("text", "N/A")
            wind_speed = current.get("wind_mph", "N/A")
            wind_dir = current.get("wind_dir", "N/A")
            uv_index = current.get("uv", "N/A")
            max_temp = forecast.get("maxtemp_f", "N/A")
            min_temp = forecast.get("mintemp_f", "N/A")
            precipitation = forecast.get("daily_chance_of_rain", "N/A")
            icon_path = condition_data.get("icon", "")
            icon_url = f"http:{icon_path}"

            self.gui.errors.setText("")
            self.gui.city.setText(f"City: {city_name}")
            self.gui.state.setText(f"State/Region: {region_name}, {country}")
            self.gui.dateandtime.setText(f"Date + Time: {date_time}")
            self.gui.temperature.setText(f"Temperature: {temperature}°F")
            self.gui.condition.setText(f"Condition: {condition}")
            self.gui.windspeed.setText(f"Windspeed: {wind_speed} mph")
            self.gui.winddirection.setText(f"Wind Direction: {wind_dir}")
            self.gui.uv.setText(f"UV Index: {uv_index}")
            self.gui.maxtemp.setText(f"Max Temp: {max_temp}°F")
            self.gui.mintemp.setText(f"Min Temp: {min_temp}°F")
            self.gui.chanceofrain.setText(f"Chance of Rain: {precipitation}%")

            try:
                pixmap = QPixmap()
                pixmap.loadFromData(requests.get(icon_url).content)
                self.gui.conditionicon.setPixmap(pixmap)
                self.gui.conditionicon.setScaledContents(True)
            except:
                self.gui.errors.setText("Error: Unable to load weather icon.")

            suggestions = self.clothingsuggestions(temperature, condition, uv_index)
            self.gui.whattowear.setText(suggestions)
        except:
            self.gui.errors.setText("Error: Unable to update UI with weather data.")
            self.hidegui()

    def clothingsuggestions(self, temperature, condition, uv_index) -> str:

        """
     Gives clothing suggestions based on the temperature, weather condition, and UV index.
        """

        try:
            temperature = float(temperature)
        except ValueError:
            return "Unable to suggest clothing due to invalid temperature."

        suggestions = []

        if temperature < 40:
            suggestions.append("Wear a heavy coat, insulated gloves, a thick scarf, and a wool hat to stay warm in the cold.")
        elif 40 <= temperature < 60:
            suggestions.append( "A light jacket, a sweater, and long pants are suitable for the cool weather.")
        elif 60 <= temperature < 80:
            suggestions.append("Wear a breathable T-shirt, shorts or lightweight pants, and comfortable shoes for mild weather.")
        else:
            suggestions.append("Wear a sleeveless shirt or tank top, shorts, and sandals or sneakers to stay cool in the heat.")

        # Condition-based suggestions
        if "rain" in condition.lower():
            suggestions.append("Carry an umbrella and wear a waterproof jacket or raincoat to stay dry.")
        if "snow" in condition.lower():
            suggestions.append("Bundle up with thermal layers, a waterproof coat, snow boots, and a hat to handle the snowy weather.")
        if "wind" in condition.lower():
            suggestions.append("Consider wearing a windbreaker or a jacket with a hood to protect against strong winds.")
        if "sun" in condition.lower():
            try:
                uv_index = float(uv_index)
                if uv_index > 7:
                    suggestions.append("Protect your skin with sunscreen (SPF 30 or higher), wear sunglasses, and a wide-brimmed hat.")
                else:
                    suggestions.append("You may still want sunglasses and sunscreen for sun protection.")
            except (ValueError, TypeError):
                suggestions.append("It looks sunny outside! Protect yourself with sunglasses and sunscreen.")

        return " ".join(suggestions)
