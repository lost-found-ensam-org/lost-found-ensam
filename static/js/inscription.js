/* inscription.js — Lost & Found ENSAM Rabat */

function togglePassword(inputId, iconId) {
    const input = document.getElementById(inputId);
    const icon  = document.getElementById(iconId);
    if (input.type === 'password') {
        input.type = 'text';
        icon.classList.replace('fa-eye-slash', 'fa-eye');
    } else {
        input.type = 'password';
        icon.classList.replace('fa-eye', 'fa-eye-slash');
    }
}

function toggleForms() {
    const formInscription = document.getElementById('form-inscription');
    const formConnexion = document.getElementById('form-connexion');

    if (formInscription.style.display !== 'none') {
        formInscription.style.display = 'none';
        formConnexion.style.display = 'block';
    } else {
        formConnexion.style.display = 'none';
        formInscription.style.display = 'block';
    }
}

// Validation personnalisée pour l'email
document.addEventListener("DOMContentLoaded", function() {
    const emails = document.querySelectorAll('input[type="email"]');
    
    emails.forEach(emailInput => {
        emailInput.addEventListener("input", function() {
            if (this.value === "") {
                this.setCustomValidity("");
            } else if (!this.value.endsWith("um.ac.ma")) {
                this.setCustomValidity("Veuillez utiliser votre adresse institutionnelle se terminant par um.ac.ma");
            } else {
                this.setCustomValidity("");
            }
        });
    });
});
