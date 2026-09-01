import win32com.client

def check_windows_updates():
    # Connect to the Windows Update session via COM
    session = win32com.client.Dispatch("Microsoft.Update.Session")
    searcher = session.CreateUpdateSearcher()

    # Search for missing/available updates
    result = searcher.Search("IsInstalled=0")

    print(f"Found {result.Updates.Count} available updates:")
    for update in result.Updates:
        print(update.Title)

def download_windows_updates():
    # Connect to the Windows Update session via COM
    session = win32com.client.Dispatch("Microsoft.Update.Session")
    searcher = session.CreateUpdateSearcher()

    # Search for missing/available updates
    result = searcher.Search("IsInstalled=0")

    print(f"Found {result.Updates.Count} available updates. Downloading...")

    downloader = session.CreateUpdateDownloader()
    downloader.Updates = result.Updates
    downloader.Download()

    print("Download completed.")

def install_windows_updates():
    # Connect to the Windows Update session via COM
    session = win32com.client.Dispatch("Microsoft.Update.Session")
    searcher = session.CreateUpdateSearcher()

    # Search for missing/available updates
    result = searcher.Search("IsInstalled=0")

    print(f"Found {result.Updates.Count} available updates. Installing...")

    installer = session.CreateUpdateInstaller()
    installer.Updates = result.Updates
    installation_result = installer.Install()

    print(f"Installation completed with result code: {installation_result.ResultCode}")