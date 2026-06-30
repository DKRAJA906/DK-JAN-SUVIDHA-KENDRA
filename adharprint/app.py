from flask import Flask, render_template, request, send_file
import fitz  # PyMuPDF
from PIL import Image
import io

app = Flask(__name__, template_folder='.')

@app.route('/')
def index():
    # यह फ्रंटएंड (HTML) को लोड करेगा
    return render_template('adhar.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file uploaded", 400
        
    file = request.files['file']
    
    # 1. पीडीएफ को मेमोरी में पढ़ें
    pdf_bytes = file.read()
    
    try:
        # 2. PyMuPDF से पीडीएफ खोलें और पहले पेज को इमेज बनाएं
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        page = doc.load_page(0)
        
        # 300 DPI पर हाई क्वालिटी इमेज जनरेट करें
        pix = page.get_pixmap(dpi=300)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        
        # 3. इमेज को क्रॉप करना 
        # (ध्यान दें: ये कोऑर्डिनेट्स (left, top, right, bottom) आपको अपनी पीडीएफ के हिसाब से एक बार सेट करने होंगे)
        crop_box = (250, 1600, 2250, 2200) 
        cropped_img = img.crop(crop_box)
        
        # 4. आउटपुट को JPEG फॉर्मेट में मेमोरी में सेव करें
        img_byte_arr = io.BytesIO()
        cropped_img.save(img_byte_arr, format='JPEG', quality=95)
        img_byte_arr.seek(0)
        
        # 5. कटी हुई इमेज को वापस फ्रंटएंड पर भेजें
        return send_file(img_byte_arr, mimetype='image/jpeg')
        
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(debug=True)
