// static/js/cart.js

document.addEventListener("DOMContentLoaded", function () {
  const minusBtn = document.querySelector(".qty-btn.left");
  const plusBtn = document.querySelector(".qty-btn.right");
  const qtyInput = document.querySelector(".quantity input");
  const buyNowBtn = document.querySelector(".buy-btn");

  // Decrease quantity
  minusBtn.addEventListener("click", () => {
    let value = parseInt(qtyInput.value) || 0;
    if (value > 0) {
      qtyInput.value = value - 1;
      updateCart();
    }
  });

  // Increase quantity
  plusBtn.addEventListener("click", () => {
    let value = parseInt(qtyInput.value) || 0;
    qtyInput.value = value + 1;
    updateCart();
  });

  // Redirect to cart when "Buy Now" clicked
  buyNowBtn.addEventListener("click", () => {
    window.location.href = "/cart"; // change path to your cart page
  });

  // Update cart logic (basic demo)
  function updateCart() {
    let qty = parseInt(qtyInput.value) || 0;
    if (qty > 0) {
      console.log("Added to cart:", qty);
      // TODO: call backend or localStorage update
    } else {
      console.log("Removed from cart");
    }
  }
});
