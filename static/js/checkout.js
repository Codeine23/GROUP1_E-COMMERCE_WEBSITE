const form = document.getElementById("checkout-form");
const button = document.getElementById("place-order-button");

function checkForm() {
    const requiredFields = form.querySelectorAll("input[required]");
    let allFilled = true;

    requiredFields.forEach((input) => {
        if (!input.value.trim()) allFilled = false;
    });

    //button.disabled = !allFilled;
}

form.addEventListener("input", checkForm);
checkForm(); // initial check
