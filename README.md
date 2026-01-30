StockFlow SPA - Smart Inventory Management with Asynchronous Architecture
Introduction

My CS50x final project is StockFlow, a web application designed to simplify the inventory management of small businesses. The idea originated from observing that many current tools are either too complex or slow for users. My objective was to create a solution that is not only functional for registering transactions, but also offers a fluid and modern user experience, similar to a desktop app.

Dynamic Interface and User Experience

The most distinctive feature of StockFlow is the integration of asynchronous components within its main views. Instead of relying on traditional form submissions that refresh the entire page, I implemented AJAX and the Fetch API to handle transactions and stock updates. This allows the user to register purchases or sales and see the inventory reflected instantly without losing their place, making the workflow much smoother and eliminating unnecessary flickering.

Technologies and Technical Stack

For the backend, I implemented Python with Flask, taking advantage of its lightweight nature to manage routes and business logic. Data persistence is handled through SQLite, where I designed a relational schema that connects products with transaction logs.

For the frontend, the challenge was even greater. I used asynchronous JavaScript to manage server requests. Every time a section is requested, Flask detects if it is an AJAX request and responds by sending only the necessary HTML fragment, which is then injected into the page's DOM. For the visual design, I used Bootstrap 5, ensuring the tool is fully responsive and easy to use on both computers and mobile devices.

Critical Features and Data Logic

The application goes beyond simple data entry; it implements specific business logic to assist the user. One of the most important features is the Low Stock Alert system. I programmed a conditional logic that evaluates the current quantity of each item against a safety threshold. If a product’s stock falls below this level, the interface provides a visual notification, preventing potential out-of-stock scenarios.

Additionally, the system performs automated financial calculations. By dynamically multiplying the unit price by the current quantity, the app provides the "Total Inventory Value" in real-time. To ensure data integrity, I also implemented a Transaction Audit Log. Every time a user buys or sells an item, the database doesn't just update the stock; it also creates a unique record in the activity table with a timestamp. This creates a transparent history that allows the user to track every change made to their assets, reducing human error and improving accountability.

Challenges and Final Thoughts

One of the main challenges was finding the right balance between a multi-page structure and asynchronous updates. I decided to keep Index and Logs as separate routes to ensure better data organization and simpler navigation, while using JavaScript to handle the heavy interaction inside each page. This project allowed me to solidify my knowledge of SQL, Flask, and the DOM. The result is a robust tool that combines the stability of a classic backend with the speed of modern web techniques.

You can see a demostration of the app in action in the following link:
[Watch the video here](https://youtu.be/BSRfLEa5_W4)
