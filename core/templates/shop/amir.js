const priceValueEl = document.getElementById('price-value');

function handleColorSelection(buttonElement) {
    if (!buttonElement || buttonElement.classList.contains('active-cs')) return;

    // Deactivate all other buttons
    colorButtonContainer.querySelectorAll('.color-option').forEach(btn => btn.classList.remove('active-cs'));
    // Activate the clicked one
    buttonElement.classList.add('active-cs');

    // Get data from the selected button
    const price = buttonElement.dataset.price;
    const colorValue = buttonElement.dataset.colorValue;
    const colorId = buttonElement.dataset.colorId;
    const inventoryId = buttonElement.dataset.colorInventoryId;

    // --- Perform all updates ---
    // 1. Update Price
    if (priceValueEl) {
        priceValueEl.textContent = price;
    }
    // 2. Update SKU
    updateSku(colorValue);
    // 3. Update Gallery
    const filteredImages = productImages.filter(img => img.color === colorValue);
    initSwiper(filteredImages);
    // 4. Update "Add to Cart" button
    if (addToCartBtn) {
        addToCartBtn.setAttribute('onclick', `addToCart('${OBJECT_ID}', '${colorId}', '${inventoryId}')`);
    }
}