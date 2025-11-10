import os
import uuid
from flask import Flask, render_template, request, jsonify
from PIL import Image
from steg_lsb import hide_message_lsb_opencv, extract_message_lsb_opencv
from steg_file import embed_file_in_image, extract_file_from_image
from encryption import encrypt_message, decrypt_message  # 🔹 ADDED

app = Flask(__name__)
app.secret_key = 'your-secret-key'

UPLOAD_FOLDER = 'uploads'
STATIC_FOLDER = 'static'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(STATIC_FOLDER, exist_ok=True)

# ---------------------------
# Existing route: get_color_mode
# ---------------------------
@app.route("/get_color_mode", methods=["POST"])
def get_color_mode():
    file = request.files.get("image")
    if not file:
        return jsonify({"error": "No image provided"}), 400
    temp_path = os.path.join(UPLOAD_FOLDER, f"temp_{uuid.uuid4().hex[:8]}_{file.filename}")
    file.save(temp_path)
    try:
        with Image.open(temp_path) as img:
            mode = img.mode
        os.remove(temp_path)
        return jsonify({"color_mode": mode})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------------------------
# EMBED PAGE
# ---------------------------
@app.route("/", methods=["GET", "POST"])
def embed():
    color_mode = None
    success = None
    filename = None
    error = None

    if request.method == "POST":
        uploaded_file = request.files.get("image")
        message_file = request.files.get("messageFile")
        message_text = request.form.get("message")
        input_option = request.form.get("inputOption")
        encrypt_toggle = request.form.get("encryption_toggle")  # 🔹 ADDED

        if not uploaded_file:
            return render_template("index.html", error="⚠️ Please upload a cover image.")

        image_filename = f"{uuid.uuid4().hex[:8]}_{uploaded_file.filename}"
        image_path = os.path.join(UPLOAD_FOLDER, image_filename)
        uploaded_file.save(image_path)

        try:
            with Image.open(image_path) as img:
                color_mode = img.mode
        except Exception as e:
            color_mode = f"Unknown ({e})"

        try:
            # If message comes from a file
            if input_option == "file" and message_file:
                msg_filename = f"{uuid.uuid4().hex[:8]}_{message_file.filename}"
                message_path = os.path.join(UPLOAD_FOLDER, msg_filename)
                message_file.save(message_path)
                ext = os.path.splitext(message_path)[1].lower()
                if ext in [".txt", ".csv", ".log"]:
                    with open(message_path, "r", encoding="utf-8") as f:
                        message = f.read()
                    # 🔹 Apply encryption toggle
                    if encrypt_toggle == "on":
                        message = encrypt_message(message)
                    filename = hide_message_lsb_opencv(image_path, message)
                    success = True
                    return render_template("index.html", success=success, filename=filename, color_mode=color_mode)
                else:
                    # For non-text file embedding, just call existing function
                    output_name = f"stego_{uuid.uuid4().hex[:8]}.png"
                    output_path = os.path.join(STATIC_FOLDER, output_name)
                    final_path = embed_file_in_image(image_path, message_path, output_path)
                    success = True
                    filename = os.path.basename(final_path)
                    return render_template("index.html", success=success, filename=filename, color_mode=color_mode)
            else:
                # Plain text input
                message = message_text or ""
                #Apply encryption toggle
                if encrypt_toggle == "on":
                    message = encrypt_message(message)
                filename = hide_message_lsb_opencv(image_path, message)
                success = True
                return render_template("index.html", success=success, filename=filename, color_mode=color_mode)
        except Exception as e:
            error = f"⚠️ {str(e)}"
            return render_template("index.html", error=error, color_mode=color_mode)

    return render_template("index.html", success=success, filename=filename, color_mode=color_mode)

# ---------------------------
# EXTRACT PAGE
# ---------------------------
@app.route("/extract", methods=["GET", "POST"])
def extract():
    message = None
    download_filename = None
    error = None

    if request.method == "POST":
        image = request.files.get("image")
        decrypt_toggle = request.form.get("decryption_toggle")  # 🔹 ADDED
        if image:
            image_filename = f"{uuid.uuid4().hex[:8]}_{image.filename}"
            image_path = os.path.join(UPLOAD_FOLDER, image_filename)
            image.save(image_path)
            try:
                extracted_raw = extract_message_lsb_opencv(image_path)
                # 🔹 Apply decryption toggle
                if decrypt_toggle == "on":
                    try:
                        message = decrypt_message(extracted_raw)
                    except Exception:
                        message = "[⚠️ Decryption failed]"
                else:
                    message = extracted_raw

                download_filename = f"extracted_{uuid.uuid4().hex[:8]}.txt"
                with open(os.path.join(STATIC_FOLDER, download_filename), "w", encoding="utf-8") as f:
                    f.write(message)
            except Exception as e:
                error = f"⚠️ {str(e)}"
        else:
            error = "⚠️ Please upload a stego image."

    return render_template("index2.html", message=message, download_filename=download_filename, error=error)

# ---------------------------
# Existing routes for file embedding/extraction remain unchanged
# ---------------------------
@app.route("/embed_file", methods=["GET", "POST"])
def embed_file_route():
    if request.method == "POST":
        cover_img = request.files.get("cover_image")
        secret_file = request.files.get("secret_file")
        output_name = request.form.get("output_name") or f"stego_{uuid.uuid4().hex[:8]}.png"
        output_path = os.path.join(STATIC_FOLDER, output_name)

        if not cover_img or not secret_file:
            return render_template("index.html", error="⚠️ Please provide both cover image and file.")

        try:
            cover_path = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4().hex[:8]}_{cover_img.filename}")
            file_path = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4().hex[:8]}_{secret_file.filename}")
            cover_img.save(cover_path)
            secret_file.save(file_path)
            final_path = embed_file_in_image(cover_path, file_path, output_path)
            return render_template("index.html", success=True, filename=os.path.basename(final_path))
        except Exception as e:
            return render_template("index.html", error=f"⚠️ {str(e)}")

    return render_template("index.html")

@app.route("/extract_file", methods=["GET", "POST"])
def extract_file_route():
    message = None
    download_filename = None
    error = None

    if request.method == "POST":
        stego_img = request.files.get("stego_image")
        if stego_img:
            stego_path = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4().hex[:8]}_{stego_img.filename}")
            stego_img.save(stego_path)
            try:
                base_name = f"recovered_{uuid.uuid4().hex[:8]}"
                final_path = extract_file_from_image(stego_path, os.path.join(STATIC_FOLDER, base_name))
                download_filename = os.path.basename(final_path)
            except Exception as e:
                error = f"⚠️ {str(e)}"
        else:
            error = "⚠️ Please upload a stego image."

    return render_template("index2.html", message=message, download_filename=download_filename, error=error)

if __name__ == "__main__":
    app.run(debug=True)
