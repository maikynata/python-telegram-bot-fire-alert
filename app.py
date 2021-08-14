from flask import Flask, render_template

app = Flask(__name__, static_folder='static', static_url_path='')

@app.route("/")
def index():
    
    # Render HTML with count variable
    return app.send_static_file("index.html")

if __name__ == "__main__":
    app.run()