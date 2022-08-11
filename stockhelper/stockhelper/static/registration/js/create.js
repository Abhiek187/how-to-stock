const passwordInputs = document.querySelectorAll("input[type=password]");
const showPasswordCheckbox = document.getElementById("showPassword");

showPasswordCheckbox.addEventListener("change", () => {
    for (const passwordInput of passwordInputs) {
        // When checked, reveal the password input
        // When unchecked, hide the password input
        passwordInput.type = showPasswordCheckbox.checked ? "text" : "password";
    }
});
