from ui import create_dash_app


dash_app = create_dash_app()

dash_app.run(debug=True, port=8040, use_reloader=False)

