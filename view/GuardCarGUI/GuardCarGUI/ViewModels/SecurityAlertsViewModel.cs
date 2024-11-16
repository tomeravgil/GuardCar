using System.Reactive;
using ReactiveUI;

public class SecurityAlertsViewModel : ReactiveObject
{
    public ReactiveCommand<Unit, Unit> NavigateToAlertsCommand { get; }
    public ReactiveCommand<Unit, Unit> NavigateToWarningsCommand { get; }

    public SecurityAlertsViewModel()
    {
        NavigateToAlertsCommand = ReactiveCommand.Create(NavigateToAlerts);
        NavigateToWarningsCommand = ReactiveCommand.Create(NavigateToWarnings);
    }

    private void NavigateToAlerts()
    {
        // Code to navigate to the Alerts page
    }

    private void NavigateToWarnings()
    {
        // Code to navigate to the Warnings page
    }
}