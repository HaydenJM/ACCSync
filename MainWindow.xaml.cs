using System;
using System.Windows;
using System.Threading.Tasks;

namespace ACCSync
{
    public partial class MainWindow : Window
    {
        private LiverySync _livelySync;
        private bool _isSyncing = false;

        public MainWindow()
        {
            InitializeComponent();
            _livelySync = new LiverySync();
            UpdateInfoLabel();
        }

        private void UpdateInfoLabel()
        {
            InfoLabel.Text = $"Liveries folder: {_livelySync.DocsPath}";
        }

        private void SyncButton_Click(object sender, RoutedEventArgs e)
        {
            if (_isSyncing)
                return;

            _isSyncing = true;
            SyncButton.IsEnabled = false;
            ProgressBar.Value = 0;
            StatusLabel.Text = "Syncing...";
            StatusLabel.Foreground = new System.Windows.Media.SolidColorBrush(System.Windows.Media.Color.FromRgb(0, 120, 215));

            Task.Run(async () =>
            {
                var (success, message) = await _livelySync.SyncLiveries(UpdateProgress);

                Dispatcher.Invoke(() =>
                {
                    _isSyncing = false;
                    SyncButton.IsEnabled = true;

                    if (success)
                    {
                        StatusLabel.Text = message;
                        StatusLabel.Foreground = new System.Windows.Media.SolidColorBrush(System.Windows.Media.Color.FromRgb(16, 124, 16));
                        MessageBox.Show(message, "Success", MessageBoxButton.OK, MessageBoxImage.Information);
                    }
                    else
                    {
                        StatusLabel.Text = "Sync failed";
                        StatusLabel.Foreground = new System.Windows.Media.SolidColorBrush(System.Windows.Media.Color.FromRgb(200, 0, 0));
                        MessageBox.Show(message, "Error", MessageBoxButton.OK, MessageBoxImage.Error);
                    }
                });
            });
        }

        private void UpdateProgress(string message, int progress)
        {
            Dispatcher.Invoke(() =>
            {
                ProgressText.Text = message;
                ProgressBar.Value = progress;
            });
        }
    }
}
