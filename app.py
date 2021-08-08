from flask import Flask, render_template

app = Flask(__name__, static_folder='static', static_url_path='')

@app.route("/")
def index():
    
    # Load current count
    f = open("count.txt", "r")
    count = int(f.read())
    f.close()

    # Increment the count
    count += 1

    # Overwrite the count
    f = open("count.txt", "w")
    f.write(str(count))
    f.close()

    # Render HTML with count variable
    return app.send_static_file("index.html")

if __name__ == "__main__":
    app.run()