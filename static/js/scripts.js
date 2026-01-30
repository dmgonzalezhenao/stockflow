/**
 * CS50x Final Project: Dynamic Inventory Management System
 * * This script handles the client-side logic for a Single Page Application (SPA) experience.
 * It manages asynchronous data fetching (AJAX) to update the dashboard and inventory
 * tables without full page reloads.
 * * Key functionalities:
 * - Form submission handling via Fetch API for adding products and logging transactions.
 * - Dynamic table pagination and content injection.
 * - Real-time UI updates for inventory summaries and stock alerts.
 * - Modal management using Bootstrap 5.
 * * @author Daniel González
 * @version 1.0.0
 */

// Waits for load content
document.addEventListener("DOMContentLoaded", () => {
    // Form element selectors for asynchronous operations (Add, Buy, and Sell)
    const addProductForm = document.getElementById("form-add-product");
    const buyProductForm = document.getElementById("form-buy-product");
    const sellProductForm = document.getElementById("form-sell-product");

    // Next will be a if's sequences for add, buy and sell forms
    // Only executes code when the modal form is deployed

    // Add Product Logic (if form has value)
    if (addProductForm) {
        // Waits for clicking submit
        addProductForm.addEventListener("submit", async (e) => {
            // Doesn't reload page
            e.preventDefault();

            // Gets data from add_product form (Name, SKU, Price, and optional Actual Stock and Minimal Stock)
            const formData = new FormData(addProductForm);

            try {
                // Sends form values to add_product route
                const response = await fetch("/add_product", {
                    method: "POST",
                    body: formData
                });

                // Waits the promise from buy route (Always give a success value)
                const result = await response.json();

                // If success = true
                if (result.success) {
                    // Updates the products table and recalculates Dashboard Summary (If product has actual stock)
                    updateProductTable(result.product);
                    updateDashboardSummary(result.summary);

                    // Add the new product to a select list for buying and selling
                    addProductToSelect(result.product);

                    // Returns a success alert, with the message from buy route
                    showAlert(result.message, "success");

                    // Resets form and hides add product modal
                    addProductForm.reset();
                    bootstrap.Modal.getInstance(document.getElementById('modalAddProduct')).hide();
                }

                // Alerts if something goes wrong with logic.py
                else {
                    showAlert(result.message, "danger");
                }
            }

            // If something goes wrong into connection to app.py
            catch (error) {
                console.error("Error:", error);
                showAlert("Critical connection error", "danger");

            }
        });
    }

    // If buy form has value
    if (buyProductForm) {
        // Waits for clicking submit
        buyProductForm.addEventListener("submit", async (e) => {
            // Doesn't reload page
            e.preventDefault();

            // Gets data from buy form (Product's id and stock to buy)
            const formData = new FormData(buyProductForm);

            try {
                // Sends the form data to buy route
                const response = await fetch("/buy", {
                    method: "POST",
                    body: formData
                });

                // Awaits for promise from app.py (It has a success attribute)
                const result = await response.json();

                // If success is true
                if (result.success) {
                    // Status persistance (To not change page on products table)
                    // Gets the url params
                    const urlParams = new URLSearchParams(window.location.search);

                    // Searches the value of page param (Is it's invalid, returns 1)
                    const currentPage = urlParams.get('page') || 1;

                    // Loads the page asychronically on user's actual page
                    loadPage('stock-container', '/?page=' + currentPage);

                    // Updates product's stock value
                    updateStockUI(result.product_id, result.new_stock, result.status);

                    // Updates Dashboard Summary
                    updateDashboardSummary(result.summary);

                    // Updates select list stock
                    updateSelectsStock(result.product_id, result.new_stock);

                    // Show a success alert
                    showAlert(result.message, "success");

                    // Resets form and hides buy modal
                    buyProductForm.reset();
                    bootstrap.Modal.getInstance(document.getElementById('modalBuyProduct')).hide();
                }

                // Return a danger alert if an error occurs into app.py logic
                else {
                    showAlert(result.message, "danger");
                }
            }

            // If something goes wrong into connection between scripts and app.py
            catch (error) {
                console.error("Buy error", error);
                showAlert("Connection Error", "danger");
            }
        });
    }

    // If the form sell exists
    if (sellProductForm) {
        // Waits for clicking submit
        sellProductForm.addEventListener("submit", async (e) => {

            // Doesn't reload page
            e.preventDefault();

            // Gets form data (Product's id and stock to sell)
            const formData = new FormData(sellProductForm);

            try {
                // Sends the form data to sell route
                const response = await fetch("/sell", {
                    method: "POST",
                    body: formData
                });

                // Waits the JSON (It has a success boolean value to validate sell)
                const result = await response.json();

                // If success value is True
                if (result.success) {
                    // Status persistance (To not change page on products table)
                    // Gets the url params
                    const urlParams = new URLSearchParams(window.location.search);

                    // Gets page value, if it's invalid, return 1
                    const currentPage = urlParams.get('page') || 1;

                    // Load table on current page
                    loadPage('stock-container', '/?page=' + currentPage);

                    // Updates the product's stock, and validates ig the new value es bigger than reorder or not
                    updateStockUI(result.product_id, result.new_stock, result.status);

                    // Updates the dashboard summary (Updates total value and low stock)
                    updateDashboardSummary(result.summary);

                    // Updates the select section for new transaction or actions
                    updateSelectsStock(result.product_id, result.new_stock);

                    // Shows a success alert and resets form
                    showAlert(result.message, "success");
                    sellProductForm.reset();

                    // Authomatically hides modal
                    const modalElement = document.getElementById('modalSellProduct');
                    const modal = bootstrap.Modal.getInstance(modalElement);
                    modal.hide();

                } else {
                    // If something is wrong on data insertion or data values
                    showAlert(result.message, "danger");
                }
            }

            // If something goes wrong with connection
            catch (error){
                console.error("Sell error:", error);
                showAlert("Error connection.", "danger");
            }
        });
    }
    // VISUAL VALIDATION FOR SELL SELECTION
    // Validates that stock is a valid value and product has enough stock
    // Gets product's id, and stock to sell for stock calculation
    const sellSelect = document.getElementById("sell-product-id");
    const sellInput = document.getElementById("sell-quantity");

    // Gets a stock warning that's a text with the new stock after sell
    const stockWarning = document.getElementById("stock-warning");

    // Gets the confirm sell button
    const btnSell = document.getElementById("btn-sell-confirm");

    // Only executes if product and input exists
    if (sellSelect && sellInput) {
        // Waits to user to select a product
        sellSelect.addEventListener("change", () => {
            // Gets id's chosen value
            const selectedOption = sellSelect.options[sellSelect.selectedIndex];

            // Gets it's actual stock by id (If doesn't have, return zero)
            const currentStock = parseInt(selectedOption.getAttribute("data-stock") || 0);

            // Now max of sellInput it's the actual stock
            sellInput.max = currentStock;

            // Adds to stockWarning a HTML text to show the new stock
            stockWarning.innerHTML = `Actual Stock: <strong>${currentStock}</strong> units.`;

            // If current stock is zero or it's an invalid value, disable sell option
            if (currentStock <= 0) {
                // Disable sell input and sell button
                sellInput.disabled = true;
                btnSell.disabled = true;

                // Updates stockWarning class and value to show to the user
                stockWarning.className = "form-text text-danger";
                stockWarning.innerText = "Out of stock! Cannot sell.";
            } else {
                // Else validate the sell action
                sellInput.disabled = false;
                btnSell.disabled = false;
                stockWarning.className = "form-text text-success";
            }
        });

        // Waits user to input the stock to sell
        sellInput.addEventListener("input", () => {
            // Gets again product's id and it's actual stock
            const selectedOption = sellSelect.options[sellSelect.selectedIndex];
            const currentStock = parseInt(selectedOption.getAttribute("data-stock") || 0);

            // Gets the input from sellInput (If it's an invalid value or None, return zero)
            const sellValue = parseInt(sellInput.value || 0);

            // If the input is bigger than stock product, don't allow to sell
            if (sellValue > currentStock) {
                // Updates the stockWarning class and text
                stockWarning.className = "form-text text-danger fw-bold";
                stockWarning.innerText = `¡Error! You only have ${currentStock} units.`;

                // IMPORTANT: Disable the sell button
                btnSell.disabled = true;
            } else {
                // If everything is good, shows the new stock (currentStock - value)
                stockWarning.className = "form-text text-success";
                stockWarning.innerHTML = `Remain stock after sell: <strong>${currentStock - sellValue}</strong>`;

                // Allow the sell button (If value is empty doesn't allow the user to sell the product)
                btnSell.disabled = false;
            }
        });
    }
});

// -- GLOBAL FUNCTIONS --

// Update the products table
function updateProductTable(product) {
    // Gets the table and a message if there's no products (Once you add one, you cannot delete them)
    const tableBody = document.getElementById("products-table-body");
    const noProductsMsg = document.getElementById("no-products-msg");
    if (noProductsMsg) noProductsMsg.remove();

    // Create the row for new product, with its id
    const newRow = document.createElement("tr");
    newRow.id = `row-${product.id}`;

    // Returns a design if stock is lower than reorder level
    const isLow = product.current_stock <= product.reorder_level;
    const badgeClass = isLow ? 'bg-warning text-dark' : 'bg-success';
    const badgeText = isLow ? 'Pedir más' : 'Ok';

    // Creates the row structure
    newRow.innerHTML = `
        <td><strong id="name-${product.id}">${product.name}</strong></td>
        <td><code class="text-muted" id="sku-${product.id}">${product.sku}</code></td>
        <td class="text-end" id="price-${product.id}">$${parseFloat(product.price).toLocaleString('en-US', {minimumFractionDigits: 2})}</td>
        <td class="text-center" id="stock-${product.id}">${product.current_stock}</td>
        <td id="status-${product.id}">
            <span class="badge ${badgeClass}">${badgeText}</span>
        </td>
    `;

    // Append it to the table
    tableBody.prepend(newRow);
    newRow.style.backgroundColor = "#d1e7dd";
    setTimeout(() => newRow.style.backgroundColor = "transparent", 2000);
}

// Adds product to the select section from buy and sell modal
function addProductToSelect(product) {
    // Gets select element
    const selectors = ["buy-product-id", "sell-product-id"];

    // For each product's id
    selectors.forEach(id => {
        // Gets the select of both selectors
        const select = document.getElementById(id);

        // If it exists
        if (select) {
            // Checks if the select list already exists (A Jinja's bug fix)
            const alreadyExists = Array.from(select.options).some(opt => opt.value == product.id);

            // If doesn't exist
            if (!alreadyExists) {
                // Creates option element, that it's value is new product's id
                const option = document.createElement("option");
                option.value = product.id;

                // Add to data stock the product's current stock (If doesn't have will be zero)
                option.setAttribute("data-stock", product.current_stock);

                // Puts the text value as product's name and SKU
                option.text = `${product.name} (SKU: ${product.sku})`;

                // Add the product to select list
                select.add(option);
            }
        }
    });
}

// Function to add a log to logs table
function addActivityLog(type, description) {
    // Searches the log's list
    const logContainer = document.getElementById("activity-log");

    // Looks if there's the no activity message (When logs table is empy)
    const noActivityMsg = logContainer.querySelector(".list-group-item.text-center");

    // Remove it when the system adds a new log
    if (noActivityMsg) noActivityMsg.remove();

    // Gets the computer's time at the add log moment
    const now = new Date();
    const timestamp = now.toLocaleString();

    // Creates the new log as a unordered list element
    const newLog = document.createElement("li");

    // Sets the class and value (type and description comes from /logs route)
    newLog.className = "list-group-item border-0 border-bottom animate__animated animate__fadeInDown";
    newLog.innerHTML = `
        <div class="d-flex w-100 justify-content-between">
            <small class="fw-bold text-primary">${type}</small>
            <small class="text-muted">${timestamp}</small>
        </div>
        <p class="mb-1 small">${description}</p>
    `;

    // Adds the log to the list's start (To search more recent logs)
    logContainer.prepend(newLog);
}


// Function to update stock of the product
function updateStockUI(id, newStock, status) {
    // Gets stock and status (Ok if stock > reorder, else low stock)
    const stockCell = document.getElementById(`stock-${id}`);
    const statusCell = document.getElementById(`status-${id}`);

    // If the stockcell exists, return the new stock with design
    if (stockCell) {
        // A little effect for new value
        stockCell.innerText = newStock;
        stockCell.style.fontWeight = "bold";
        stockCell.style.color = "#198754";
        setTimeout(() => {
            stockCell.style.fontWeight = "normal";
            stockCell.style.color = "inherit";
        }, 2000);
    }

    // If already has a status (It's not a new product)
    if (statusCell) {
        // Sets status value
        const badgeClass = status === 'Ok' ? 'bg-success' : 'bg-warning text-dark';
        statusCell.innerHTML = `<span class="badge ${badgeClass}">${status}</span>`;
    }
}

// Function to update dashboard summary
function updateDashboardSummary(summary) {
    // Case if summary return is empty
    if (!summary) return;

    // Just gets every value by id
    document.getElementById("total-items").innerText = summary.total_items;
    document.getElementById("total-value").innerText = `$${parseFloat(summary.total_value).toLocaleString('en-US', {minimumFractionDigits: 2})}`;
    document.getElementById("low-stock-count").innerText = summary.low_stock_count;
}

// Function to show success or danger alerts
function showAlert(message, type) {
    // Gets the top container for alerts
    const container = document.getElementById("alert-container");

    // Creates the div "alert"
    const alert = document.createElement("div");

    // Returns the message and a button to close the alert
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    // Appends alert by max 5 seconds
    container.appendChild(alert);
    setTimeout(() => {
        const bsAlert = new bootstrap.Alert(alert);
        bsAlert.close();
    }, 5000);
}

// Function to update select stock of a product with new stock
function updateSelectsStock(productId, newStock) {
    // Gets the selectors from buy and sell select
    const selectors = ["buy-product-id", "sell-product-id"];

    selectors.forEach(selectId => {
        // Gets the ids of every product in select list
        const select = document.getElementById(selectId);

        // Looks if productId is in the select list
        const option = select?.querySelector(`option[value="${productId}"]`);

        // If it exists
        if (option) {
            // Sets the actual stock to the new one
            option.setAttribute("data-stock", newStock);
            // Updates text to allow the user to see the real stock
            const baseText = option.text.split(" (")[0];
            option.text = (selectId === 'sell-product-id')
                ? `${baseText} (Avaible: ${newStock})`
                : `${baseText} (Updated SKU)`;
        }
    });
}

// Function to load a page from logs table
function loadLogsPage(page) {
    // Fetch the logs page value, and sends Ajax's value to Flask
    fetch(`/logs?page=${page}&ajax=1`)

        // Waits response (The logs in the page)
        .then(response => response.text())
        .then(html => {
            // Sets the logs into logs-container (logs table)
            document.getElementById('logs-container').innerHTML = html;

            // Updates page url to the page value
            window.history.pushState({}, '', `/logs?page=${page}`);
        });
}

// Asynchronous function while the page is loading (It's used to load logs and products tables)
async function loadPage(containerId, url) {
    // Gets the container and changes it's opacity for user's experience
    const container = document.getElementById(containerId);
    container.style.opacity = '0.5';

    // Includes the Ajax's value to the URL for validate action in Flask
    const ajaxUrl = url.includes('?') ? `${url}&ajax=1` : `${url}?ajax=1`;

    try {
        // Waits the response and the HTML text
        const response = await fetch(ajaxUrl);
        const html = await response.text();

        // Puts the HTML into the container
        container.innerHTML = html;

        // Updates url to an empty one
        window.history.pushState({}, '', url);

    } catch (e) {
        // If someting goes wrong
        console.error("Loading Page Error:", e);
    } finally {
        // Puts opacity to 1
        container.style.opacity = '1';
    }
}
