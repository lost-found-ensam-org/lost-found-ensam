/* ═══════════════════════════════════════
   upload_preview.js
   Gestion du retour visuel et aperçu photo
   Lost & Found ENSAM Rabat
═══════════════════════════════════════ */

document.addEventListener("DOMContentLoaded", function () {
    const photoInput = document.getElementById("photo");
    const uploadBox = document.getElementById("uploadBox");
    const placeholder = document.getElementById("uploadPlaceholder");
    const preview = document.getElementById("uploadPreview");
    const previewImage = document.getElementById("previewImage");
    const fileNameEl = document.getElementById("fileName");
    const fileSizeEl = document.getElementById("fileSize");
    const btnRemove = document.getElementById("btnRemoveFile");

    if (!photoInput || !uploadBox) return;

    function formatFileSize(bytes) {
        if (bytes < 1024) return bytes + " octets";
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " Ko";
        return (bytes / (1024 * 1024)).toFixed(2) + " Mo";
    }

    function handleFile(file) {
        if (!file) return;

        // Vérification basique du type
        if (!file.type.startsWith("image/")) {
            alert("Veuillez sélectionner un fichier image valide (JPG, PNG, WEBP).");
            photoInput.value = "";
            return;
        }

        // Vérification de la taille (max 5 Mo)
        if (file.size > 5 * 1024 * 1024) {
            alert("L'image dépasse la taille limite autorisée (5 Mo).");
            photoInput.value = "";
            return;
        }

        const reader = new FileReader();
        reader.onload = function (e) {
            previewImage.src = e.target.result;
            fileNameEl.textContent = file.name;
            fileSizeEl.textContent = formatFileSize(file.size);

            placeholder.style.display = "none";
            preview.style.display = "flex";
            uploadBox.classList.add("has-file");
        };
        reader.readAsDataURL(file);
    }

    // Détection du choix de fichier
    photoInput.addEventListener("change", function () {
        if (this.files && this.files[0]) {
            handleFile(this.files[0]);
        }
    });

    // Bouton pour retirer / changer la photo
    if (btnRemove) {
        btnRemove.addEventListener("click", function (e) {
            e.stopPropagation();
            photoInput.value = "";
            previewImage.src = "";
            fileNameEl.textContent = "";
            fileSizeEl.textContent = "";

            preview.style.display = "none";
            placeholder.style.display = "block";
            uploadBox.classList.remove("has-file");
        });
    }

    // Gestion Drag & Drop
    ["dragenter", "dragover"].forEach(eventName => {
        uploadBox.addEventListener(eventName, function (e) {
            e.preventDefault();
            e.stopPropagation();
            uploadBox.classList.add("drag-over");
        }, false);
    });

    ["dragleave", "drop"].forEach(eventName => {
        uploadBox.addEventListener(eventName, function (e) {
            e.preventDefault();
            e.stopPropagation();
            uploadBox.classList.remove("drag-over");
        }, false);
    });

    uploadBox.addEventListener("drop", function (e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files && files[0]) {
            photoInput.files = files;
            handleFile(files[0]);
        }
    });
});

