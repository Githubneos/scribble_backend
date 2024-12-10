from flask import Flask, jsonify
from flask_cors import CORS

# initialize a flask application (app)
app = Flask(__name__)
CORS(app, supports_credentials=True, origins='*')  # Allow all origins (*)

# ... your existing Flask

# add an api endpoint to flask app
@app.route('/api/Keerthan')
def get_data():
    # start a list, to be used like a information database
    InfoDb = []

    # add a row to list, an Info record
    InfoDb.append({
        "FirstName": "Keerthan",
        "LastName": "Karumudi",
        "DOB": "December 24",
        "Residence": "San Diego",
        "Email": "keerthansaikarumudi@stu.powayusd.com",
        "Favorite_Movies": [ "Hangover, Superbad, Jurassic Park, Ted"]
    })

    # add a row to list, an Info record
    InfoDb.append({
        "FirstName": "Maxwell",
        "LastName": "Gaudinez",
        "DOB": "January 31",
        "Residence": "San Diego",
        "Email": "maxwellg56824@stu.powayusd.com",
        "Owns_Cars": ["2022_BMW_X6, Volvo_XC90, Volvo_S60, Mercedes_GLE350"]
    })
        
    InfoDb.append({
        "FirstName": "Daksha",
        "LastName": "Gowda",
        "DOB": "August 15",
        "Residence": "San Diego",
        "Email": "dakshag45035@stu.powayusd.com",
        "favorite_pokemon": ["Rayquaza, Yveltal, Zygarde"]
    })
    
    InfoDb.append({
        "FirstName": "Zach",
        "LastName": "Peltz",
        "DOB": "March 22",
        "Residence": "San Diego",
        "Email": "zacharyp16044@stu.powayusd.com",
        "favorite_pokemon": ["Arceus, Dialga, Lugia"]
    })
    
    InfoDb.append({
        "FirstName": "Ian",
        "LastName": "Manangan",
        "DOB": "March 7",
        "Residence": "San Diego",
        "Email": "Ianm02879@stu.powayusd.com",
        "favorite_pokemon": ["Moltres, Zapdos, Articuno"]
    })
    
    
    return jsonify(InfoDb)

# add an HTML endpoint to flask app
@app.route('/')
def say_hello():
    html_content = """
    <html>
    <head>
        <title>Hellox</title>
    </head>
    <body>
        <h2>Hello, World!</h2>
    </body>
    </html>
    """
    return html_content

if __name__ == '__main__':
    app.run(port=5002)  # Use a different port, e.g., 5002
