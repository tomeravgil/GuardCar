using System;
using Avalonia.Controls;
using Avalonia.Threading;

namespace GuardCarGUI.Views
{
    public partial class Weather : UserControl
    {
        private WeatherViewModel _viewModel;

        public Weather()
        {
            InitializeComponent();
            _viewModel = new WeatherViewModel();
            DataContext = _viewModel;

            // Periodically update weather data
            var timer = new DispatcherTimer { Interval = TimeSpan.FromMinutes(30) };
            timer.Tick += OnTimerTick;
            timer.Start();
        }

        private async void OnTimerTick(object? sender, EventArgs e)
        {
            try
            {
                await _viewModel.UpdateWeatherData();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error during periodic update: {ex.Message}");
            }
        }

    }
}