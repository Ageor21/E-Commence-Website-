// 1. Quantity Validation
document.addEventListener("DOMContentLoaded", () => {
    const quantityInputs = document.querySelectorAll("input[type='number']");

    quantityInputs.forEach(input => {
        input.addEventListener("input", () => {
            const max = parseInt(input.max, 10);
            const min = parseInt(input.min, 10);
            const value = parseInt(input.value, 10);

            if (value > max) {
                input.value = max;
                alert(`You cannot order more than ${max} units.`);
            } else if (value < min) {
                input.value = min;
                alert(`The minimum quantity is ${min}.`);
            }
        });
    });
});

// 2. Flash Message Auto-Dismissal
document.addEventListener("DOMContentLoaded", () => {
    const flashMessages = document.querySelectorAll(".flash-message");
    if (flashMessages) {
        setTimeout(() => {
            flashMessages.forEach(message => {
                message.style.transition = "opacity 1s";
                message.style.opacity = "0";
                setTimeout(() => {
                    message.remove();
                }, 1000);
            });
        }, 5000); // 5 seconds delay before dismissal
    }
});

// 3. Smooth Scroll for Internal Links
document.addEventListener("DOMContentLoaded", () => {
    const links = document.querySelectorAll("a[href^='#']");
    links.forEach(link => {
        link.addEventListener("click", e => {
            e.preventDefault();
            const target = document.querySelector(link.getAttribute("href"));
            if (target) {
                target.scrollIntoView({ behavior: "smooth" });
            }
        });
    });
});

// 4. Dynamic Cart Total Update (Optional)
// This requires an editable cart table with quantity inputs
document.addEventListener("DOMContentLoaded", () => {
    const cartTable = document.querySelector("#cart-table");
    if (cartTable) {
        const updateTotal = () => {
            let total = 0;
            const rows = cartTable.querySelectorAll("tbody tr");
            rows.forEach(row => {
                const price = parseFloat(row.querySelector(".price").textContent.replace("$", ""));
                const quantity = parseInt(row.querySelector(".quantity-input").value, 10);
                total += price * quantity;
            });
            document.querySelector("#cart-total").textContent = `$${total.toFixed(2)}`;
        };

        const quantityInputs = cartTable.querySelectorAll(".quantity-input");
        quantityInputs.forEach(input => {
            input.addEventListener("input", updateTotal);
        });

        updateTotal(); // Initial calculation
    }
});
