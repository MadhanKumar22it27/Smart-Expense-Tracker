from flask import Flask, request, jsonify, render_template
import joblib
import pandas as pd
import os
from datetime import datetime  # Import datetime for current date

app = Flask(__name__)

# Load the trained model and label encoder
model = joblib.load("model.pkl")  
encoder = joblib.load("encoder.pkl")  

# Function to predict category
def predict_category(description):
    prediction = model.predict([description])  
    category = encoder.inverse_transform(prediction)[0]  
    return category

# Function to save transaction (with Date)
def save_transaction(description, amount, category, file_path="transactions.xlsx"):
    date = datetime.now().strftime("%d-%m-%Y")  # Get current date (YYYY-MM-DD)
    new_entry = pd.DataFrame([[date, description, amount, category]], columns=["Date", "Description", "Amount", "Category"])
    
    if os.path.exists(file_path):
        df = pd.read_excel(file_path)
        df = pd.concat([df, new_entry], ignore_index=True)
    else:
        df = new_entry  # Create file if not exists

    df.to_excel(file_path, index=False)

# Home route to serve the HTML page
@app.route("/")
def home():
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Expense Category Predictor</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                text-align: center;
                margin: 0;
                padding: 0;
            }
            .container {
                background: white;
                width: 40%;
                margin: 5% auto;
                padding: 20px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                border-radius: 10px;
            }
            h2 {
                color: #333;
            }
            form {
                display: flex;
                flex-direction: column;
            }
            label {
                font-size: 16px;
                margin-top: 10px;
            }
            input {
                padding: 8px;
                font-size: 16px;
                margin: 5px 0 15px;
                border: 1px solid #ccc;
                border-radius: 5px;
            }
            button {
                background: #28a745;
                color: white;
                font-size: 16px;
                padding: 10px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
            }
            button:hover {
                background: #218838;
            }
            .hidden {
                display: none;
            }
            #result {
                margin-top: 20px;
                padding: 10px;
                background: #dff0d8;
                border: 1px solid #c3e6cb;
                border-radius: 5px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Expense Category Predictor</h2>
            <form id="expenseForm">
                <label for="description">Payment Description:</label>
                <input type="text" id="description" name="description" required>

                <label for="amount">Amount:</label>
                <input type="number" id="amount" name="amount" required>

                <button type="submit">Predict Category</button>
            </form>

            <div id="result" class="hidden">
                <h3>Prediction Result</h3>
                <p><strong>Category:</strong> <span id="category"></span></p>
            </div>
        </div>

        <script>
            document.getElementById("expenseForm").addEventListener("submit", async function(event) {
                event.preventDefault();
                
                let description = document.getElementById("description").value;
                let amount = document.getElementById("amount").value;

                let response = await fetch("/predict", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ description, amount })
                });

                let data = await response.json();
                document.getElementById("category").innerText = data.category;
                document.getElementById("result").classList.remove("hidden");
            });
        </script>
    </body>
    </html>
    '''

# API endpoint to handle predictions
@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    description = data["description"]
    amount = float(data["amount"])

    category = predict_category(description)
    save_transaction(description, amount, category)  # Save with date

    return jsonify({"category": category})

if __name__ == "__main__":
    app.run(debug=True)