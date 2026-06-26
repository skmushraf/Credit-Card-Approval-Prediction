import os
import urllib.request

def download_file(url, filepath):
    print(f"Downloading {url} to {filepath}...")
    try:
        # User-agent header to avoid getting blocked
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        with urllib.request.urlopen(req) as response, open(filepath, 'wb') as out_file:
            data = response.read()
            out_file.write(data)
        print(f"Successfully downloaded {filepath} ({len(data)} bytes).")
    except Exception as e:
        print(f"Error downloading {url}: {e}")

def main():
    data_dir = r"D:\smartbridge\data"
    os.makedirs(data_dir, exist_ok=True)
    
    urls = {
        "application_record.csv": "https://raw.githubusercontent.com/damaniayesh/Credit-Card-Approval-Prediction/master/application_record.csv",
        "credit_record.csv": "https://raw.githubusercontent.com/damaniayesh/Credit-Card-Approval-Prediction/master/credit_record.csv"
    }
    
    for filename, url in urls.items():
        filepath = os.path.join(data_dir, filename)
        if not os.path.exists(filepath):
            download_file(url, filepath)
        else:
            print(f"{filename} already exists at {filepath}.")

if __name__ == "__main__":
    main()
