import win32com.client
import pythoncom
import pyuac
import subprocess
import database as db

DatabaseManager = db.DatabaseManager()

def find_updates():
    """
    Finds available Windows updates and returns them as a list of dicts.
    Each dict contains: index, title, description, kb_articles, is_downloaded.
    """
    updates_list = []
    try:
        pythoncom.CoInitialize()

        session = win32com.client.Dispatch("Microsoft.Update.Session")
        searcher = session.CreateUpdateSearcher()

        print("Searching for available updates...")
        search_result = searcher.Search("IsInstalled=0 AND Type='Software'")

        for i in range(search_result.Updates.Count):
            update = search_result.Updates.Item(i)
            if DatabaseManager.check(update.Title):  # Skip if the update is already in the database
                continue
            DatabaseManager.update_set(update.Title, update.Description)
    except Exception as e:
        print(f"Error finding updates: {e}")
    finally:
        pythoncom.CoUninitialize()

import subprocess

def find_winget_updates(db_manager):
    """
    Finds available winget package updates and stores new ones in the database.
    """
    try:
        result = subprocess.run(
            ["winget", "upgrade", "--accept-source-agreements"],
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )

        lines = result.stdout.splitlines()
        start_index = None
        for i, line in enumerate(lines):
            if line.strip().startswith("Name") and "Id" in line:
                start_index = i + 2  # skip header + separator line
                break

        if start_index is None:
            print("No winget updates found or unexpected output format.")
            return

        for line in lines[start_index:]:
            if not line.strip() or line.startswith("-"):
                continue
            parts = line.split()
            if len(parts) < 4:
                continue

            name = parts[0]
            available_version = parts[-2]  # second-to-last column is usually "Available"

            if db_manager.check(name):  # Skip if the update is already in the database
                continue
            db_manager.update_set(name, available_version)

    except Exception as e:
        print(f"Error finding winget updates: {e}")
    finally:
        print("Winget update check complete.")


def install_update_by_title(update_title):
    """
    Installs a single Windows update by matching its title (case-insensitive).
    """
    try:
        pythoncom.CoInitialize()

        session = win32com.client.Dispatch("Microsoft.Update.Session")
        searcher = session.CreateUpdateSearcher()
        search_result = searcher.Search("IsInstalled=0 AND Type='Software'")

        selected_update = None
        for i in range(search_result.Updates.Count):
            update = search_result.Updates.Item(i)
            if update_title.lower() in update.Title.lower():
                selected_update = update
                break

        if not selected_update:
            print(f"No update found matching: {update_title}")
            return False

        print(f"Selected update: {selected_update.Title}")

        updates_to_install = win32com.client.Dispatch("Microsoft.Update.UpdateColl")
        updates_to_install.Add(selected_update)

        if not selected_update.IsDownloaded:
            print("Downloading update...")
            downloader = session.CreateUpdateDownloader()
            downloader.Updates = updates_to_install
            downloader.Download()

        print("Installing update...")
        installer = session.CreateUpdateInstaller()
        installer.Updates = updates_to_install
        result = installer.Install()

        if result.ResultCode == 2:
            print("Update installed successfully.")
            return True
        else:
            print(f"Installation finished with result code: {result.ResultCode}")
            return False

    except Exception as e:
        print(f"Error installing update: {e}")
        return False
    finally:
        pythoncom.CoUninitialize()


if __name__ == "__main__":
    import ctypes
    print("Is admin:", ctypes.windll.shell32.IsUserAnAdmin())
    updates = find_winget_updates()
    if not updates:
        print("No updates available.")
    else:
        print("\nAvailable Updates:")
