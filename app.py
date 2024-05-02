from website import create_app


@app.route('/makeup')
def makeup():
    return render_template("makeup_page.html")

@app.route('/test_result', methods=['POST'])
def test_result():
    return render_template('test_result.html')

@app.route('/community')
def community():
    return render_template("community_page.html")


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)