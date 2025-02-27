import urllib.request
import json
from urllib.error import URLError

def send_image(image_path):
    try:
        # Prepare the files as multipart/form-data
        boundary = b'----WebKitFormBoundary7MA4YWxkTrZu0gW'
        headers = {
            'Content-Type': f'multipart/form-data; boundary={boundary.decode()}'
        }
        
        # Read the image file
        with open(image_path, 'rb') as f:
            img_data = f.read()
            
        # Construct the multipart form data
        data = []
        data.append(b'--' + boundary)
        data.append(b'Content-Disposition: form-data; name="file"; filename="image.png"')
        data.append(b'Content-Type: image/png')
        data.append(b'')
        data.append(img_data)
        data.append(b'--' + boundary + b'--')
        
        # Join with CRLF
        body = b'\r\n'.join(data)
        
        # Create and send the request
        req = urllib.request.Request(
            url="http://localhost:8000/parse",
            data=body,
            headers=headers,
            method='POST'
        )
        
        with urllib.request.urlopen(req) as response:
            response_data = response.read()
            return json.loads(response_data)
            
    except URLError as e:
        print(f"Error connecting to server: {e}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Example usage
if __name__ == "__main__":
    results = send_image('path/to/your/image.png')
    if results:
        print(results)