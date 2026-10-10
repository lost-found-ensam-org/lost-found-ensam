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

function showConnexionForm() {
    const formInscription = document.getElementById('form-inscription');
    const formConnexion = document.getElementById('form-connexion');
    if (formInscription && formConnexion) {
        formInscription.style.display = 'none';
        formConnexion.style.display = 'block';
    }
}

function showInscriptionForm() {
    const formInscription = document.getElementById('form-inscription');
    const formConnexion = document.getElementById('form-connexion');
    if (formInscription && formConnexion) {
        formConnexion.style.display = 'none';
        formInscription.style.display = 'block';
    }
}

// Validation personnalisée pour l'email et détection du hash pour scroll fluide
document.addEventListener("DOMContentLoaded", function() {
    const emails = document.querySelectorAll('input[type="email"]');
    
    emails.forEach(emailInput => {
        emailInput.addEventListener("input", function() {
            if (this.value === "") {
                this.setCustomValidity("");
            } else if (!this.value.endsWith("um5.ac.ma")) {
                this.setCustomValidity("Veuillez utiliser votre adresse institutionnelle se terminant par um5.ac.ma");
            } else {
                this.setCustomValidity("");
            }
        });
    });

    // Détection de l'ancre #form-container ou #connexion pour scroller directement
    const hash = window.location.hash;
    if (hash === '#form-container' || hash === '#connexion') {
        showConnexionForm();
        setTimeout(() => {
            const container = document.getElementById('form-container');
            if (container) {
                container.scrollIntoView({ behavior: 'smooth', block: 'center' });
                const loginEmail = document.getElementById('login-email');
                if (loginEmail) loginEmail.focus();
            }
        }, 150);
    } else if (hash === '#inscription') {
        showInscriptionForm();
        setTimeout(() => {
            const container = document.getElementById('form-container');
            if (container) {
                container.scrollIntoView({ behavior: 'smooth', block: 'center' });
                const nomInput = document.getElementById('nom');
                if (nomInput) nomInput.focus();
            }
        }, 150);
    }
});
