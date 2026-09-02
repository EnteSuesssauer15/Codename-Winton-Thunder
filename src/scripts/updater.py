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
            DatabaseManager.update_set(update.Title, update.Description)
    except Exception as e:
        print(f"Error finding updates: {e}")
    finally:
        pythoncom.CoUninitialize()


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
    if not pyuac.isUserAdmin():
        print("Re-launching with admin privileges...")
        pyuac.runAsAdmin()
    else: 
        updates = find_updates()

        if not updates:
            print("No updates available.")
        else:
            print("\nAvailable Updates:")
