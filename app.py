from website import create_app, request



if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)