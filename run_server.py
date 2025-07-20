from app import app

if __name__ == '__main__':
    try:
        print("Iniciando servidor Flask...")
        app.run(host='127.0.0.1', port=5000, debug=True)
    except Exception as e:
        print(f"Erro ao iniciar servidor: {e}")
        import traceback
        traceback.print_exc()
