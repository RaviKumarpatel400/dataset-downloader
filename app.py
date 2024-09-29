from flask import Flask, render_template, request, send_file
import requests
import os

app = Flask(__name__)

# Route for the homepage to display the form
@app.route('/')
def home():
    return render_template('home.html')

# Function to handle Google Sheets download URL transformation
def transform_google_sheet_url(url):
    # Check if it's a Google Sheets link
    if 'docs.google.com/spreadsheets' in url:
        try:
            # Extract the spreadsheet ID and sheet GID from the URL
            parts = url.split('/')
            spreadsheet_id = parts[5]
            gid = url.split('gid=')[1]
            # Create the downloadable CSV URL
            csv_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format=csv&gid={gid}"
            return csv_url
        except IndexError:
            return None
    return None

# Route to handle dataset downloading
@app.route('/download', methods=['POST'])
def download_dataset():
    dataset_url = request.form.get('dataset_url')

    if dataset_url:
        # Transform Google Sheets link to CSV download link if necessary
        download_url = transform_google_sheet_url(dataset_url) or dataset_url

        # Determine the filename (either from URL or default to 'dataset.csv')
        filename = download_url.split("/")[-1]
        if not filename.endswith(".csv"):
            filename = "dataset.csv"  # Fallback for Google Sheets downloads

        filepath = os.path.join("downloads", filename)

        try:
            # Download the file (Google Sheets CSV or regular CSV)
            response = requests.get(download_url, stream=True)

            # Save the file to the "downloads" folder
            with open(filepath, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:  # Filter out keep-alive new chunks
                        file.write(chunk)

            # Serve the file to the user for download
            return send_file(filepath, as_attachment=True)

        except Exception as e:
            return f"Error downloading the file: {str(e)}"

    return "No valid URL provided."

if __name__ == '__main__':
    # Create the "downloads" folder if it doesn't exist
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    
    app.run(debug=True)
