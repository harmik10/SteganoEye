// Typed.js animation
var typed = new Typed('#typed', {
    strings: ['🔐 Steganography - Hide Your Message'],
    typeSpeed: 50,
    showCursor: false
});

function previewImage(e) {
    const file = e.target.files[0];
    const preview = document.getElementById('imagePreview');
    const infoBox = document.getElementById('imageInfo');

    if (!file) return;

    preview.src = URL.createObjectURL(file);
    preview.style.display = 'block';

    const img = new Image();
    img.src = URL.createObjectURL(file);

    img.onload = function () {
        const width = img.width;
        const height = img.height;
        const fileSizeKB = (file.size / 1024).toFixed(2);
        const fileName = file.name;
        const fileType = file.type || 'Unknown';

        // show basic info first
        if (infoBox) {
            infoBox.innerHTML = `
                <strong>Image Properties:</strong><br>
                Name: ${fileName} <br>
                Type: ${fileType} <br>
                Size: ${fileSizeKB} KB <br>
                Resolution: ${width} × ${height}px <br>
                <em>Detecting color mode...</em>
            `;
            infoBox.style.display = 'block';
        }

        // call backend to get color mode
        const formData = new FormData();
        formData.append('image', file);

        fetch('/get_color_mode', {
            method: 'POST',
            body: formData
        })
        .then(res => res.json())
        .then(data => {
            if (data.color_mode) {
                infoBox.innerHTML = `
                    <strong>Image Properties:</strong><br>
                    Name: ${fileName} <br>
                    Type: ${fileType} <br>
                    Size: ${fileSizeKB} KB <br>
                    Resolution: ${width} × ${height}px <br>
                    Color Mode: <strong>${data.color_mode}</strong>
                `;
            } else if (data.error) {
                infoBox.innerHTML += `<br><strong>Error getting color mode:</strong> ${data.error}`;
            }
        })
        .catch(err => {
            infoBox.innerHTML += `<br><strong>Error:</strong> ${err}`;
        });
    };
}

function toggleLabel() {
    const toggle = document.getElementById('encryptToggle');
    const label = document.getElementById('encryptLabel');
    if (!toggle || !label) return;
    label.textContent = toggle.checked ? "Encryption" : "No Encryption";
    document.getElementById('encryptionState').value = toggle.checked ? "1" : "0";
    label.style.color = toggle.checked ? "#198754" : "#dc3545";
    
}

function toggleInputOption() {
    const textOption = document.getElementById("enterTextOption")?.checked;
    const textGroup = document.getElementById("textInputGroup");
    const fileGroup = document.getElementById("fileInputGroup");

    if (textGroup && fileGroup) {
        textGroup.style.display = textOption ? "block" : "none";
        fileGroup.style.display = textOption ? "none" : "block";
    }
}

function showNotification(message, type = 'success') {
    const toastEl = document.getElementById('notifToast');
    const toastMsg = document.getElementById('toastMessage');

    if (!toastEl || !toastMsg) return;

    if (type === 'error') {
        toastEl.className = 'toast align-items-center text-bg-danger border-0';
    } else if (type === 'warning') {
        toastEl.className = 'toast align-items-center text-bg-warning border-0';
    } else {
        toastEl.className = 'toast align-items-center text-bg-success border-0';
    }

    toastMsg.textContent = message;

    const toast = new bootstrap.Toast(toastEl, { delay: 5000 });
    toast.show();
}

document.addEventListener("DOMContentLoaded", function () {
    new Typed('#typed', {
        strings: ['🔐 Steganography - Hide Your Message'],
        typeSpeed: 50,
        showCursor: false
    });

    toggleLabel();
    toggleInputOption();
});
