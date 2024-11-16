using System;
using System.Net.Http;
using System.Text.Json;
using System.Threading.Tasks;
using ReactiveUI;

public class WeatherViewModel : ReactiveObject
{
    private string _place = "Unknown City";
    private int _temperature = 0;
    private int _highTemp = 0;
    private int _lowTemp = 0;
    private string _weatherIcon = "default_icon"; // Placeholder for weather icon
    private string _backgroundColor = "#2B2E6E";

    public string Place
    {
        get => _place;
        set => this.RaiseAndSetIfChanged(ref _place, value);
    }

    public int Temperature
    {
        get => _temperature;
        set => this.RaiseAndSetIfChanged(ref _temperature, value);
    }

    public int HighTemp
    {
        get => _highTemp;
        set => this.RaiseAndSetIfChanged(ref _highTemp, value);
    }

    public int LowTemp
    {
        get => _lowTemp;
        set => this.RaiseAndSetIfChanged(ref _lowTemp, value);
    }

    public string WeatherIcon
    {
        get => _weatherIcon;
        set => this.RaiseAndSetIfChanged(ref _weatherIcon, value);
    }

    public string BackgroundColor
    {
        get => _backgroundColor;
        set => this.RaiseAndSetIfChanged(ref _backgroundColor, value);
    }

    public WeatherViewModel()
    {
        // Call the method to update weather data on ViewModel load
        _ = Task.Run(async () => await UpdateWeatherData());
    }

    public async Task UpdateWeatherData()
    {
        try
        {
            // API endpoint with forecast data
            var apiUrl = "https://api.open-meteo.com/v1/forecast?latitude=42.7284&longitude=-73.6918&current=temperature_2m,is_day,precipitation,rain,showers,snowfall,cloud_cover,wind_speed_10m&hourly=temperature_2m,precipitation,cloud_cover&daily=temperature_2m_max,temperature_2m_min&temperature_unit=fahrenheit&timezone=America%2FNew_York&forecast_days=1";

            using (var client = new HttpClient())
            {
                var response = await client.GetStringAsync(apiUrl);
                var weatherData = JsonSerializer.Deserialize<WeatherApiResponse>(response);

                if (weatherData != null && weatherData.current != null && weatherData.daily != null)
                {
                    // Extract the data
                    Console.Write("weatherData" + weatherData.current.temperature_2m);
                    Temperature = (int)Math.Round(weatherData.current.temperature_2m);
                    HighTemp = (int)Math.Round(weatherData.daily.temperature_2m_max[0]);
                    LowTemp = (int)Math.Round(weatherData.daily.temperature_2m_min[0]);
                    Place = "Albany, NY"; // Replace with an actual lookup or predefined value
                    WeatherIcon = GetWeatherIcon(weatherData.current.cloud_cover, weatherData.current.is_day);

                    // Update the background color based on the current time from the API
                    UpdateBackgroundColor(weatherData.current.time);
                }
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error updating weather data: {ex.Message}");
        }
    }

    private void UpdateBackgroundColor(string apiTime)
    {
        // Parse the time provided by the API
        var time = DateTime.Parse(apiTime);
        var hour = time.Hour;
        var totalMinutes = hour * 60 + time.Minute;

        const int morningStart = 6 * 60; // 6:00 AM
        const int noonStart = 12 * 60;  // 12:00 PM
        const int sunsetStart = 16 * 60; // 4:00 PM
        const int nightStart = 18 * 60;  // 6:00 PM

        var morningColor = (R: 84, G: 155, B: 199); // Bright blue (#549BC7)
        var sunsetColor = (R: 204, G: 112, B: 71);  // Orange (#CC7047)
        var nightColor = (R: 43, G: 46, B: 110);    // Night blue (#2B2E6E)

        if (totalMinutes >= morningStart && totalMinutes < noonStart)
        {
            BackgroundColor = "#549BC7"; // Morning - bright blue
        }
        else if (totalMinutes >= noonStart && totalMinutes < sunsetStart)
        {
            var progress = (float)(totalMinutes - noonStart) / (sunsetStart - noonStart);
            BackgroundColor = InterpolateColor(morningColor, sunsetColor, progress);
        }
        else if (totalMinutes >= sunsetStart && totalMinutes < nightStart)
        {
            var progress = (float)(totalMinutes - sunsetStart) / (nightStart - sunsetStart);
            BackgroundColor = InterpolateColor(sunsetColor, nightColor, progress);
        }
        else
        {
            BackgroundColor = "#2B2E6E"; // Night
        }
    }

    private string InterpolateColor((int R, int G, int B) startColor, (int R, int G, int B) endColor, float progress)
    {
        int r = (int)(startColor.R + (endColor.R - startColor.R) * progress);
        int g = (int)(startColor.G + (endColor.G - startColor.G) * progress);
        int b = (int)(startColor.B + (endColor.B - startColor.B) * progress);

        return $"#{r:X2}{g:X2}{b:X2}";
    }

    private string GetWeatherIcon(int cloudCover, int isDay)
    {
        if (cloudCover > 80) return isDay == 1 ? "cloudy_day_icon" : "cloudy_night_icon";
        if (cloudCover > 50) return isDay == 1 ? "partly_cloudy_day_icon" : "partly_cloudy_night_icon";
        return isDay == 1 ? "clear_day_icon" : "clear_night_icon";
    }
}

// Define the expected structure of your API response
public class WeatherApiResponse
{
    public CurrentWeatherData current { get; set; }
    public DailyWeatherData daily { get; set; }
}

public class CurrentWeatherData
{
    public string time { get; set; }
    public double temperature_2m { get; set; } // Changed from int to double
    public int is_day { get; set; }
    public int cloud_cover { get; set; }
}

public class DailyWeatherData
{
    public double[] temperature_2m_max { get; set; } // Changed from int[] to double[]
    public double[] temperature_2m_min { get; set; } // Changed from int[] to double[]
}

