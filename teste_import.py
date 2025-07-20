try:
    import app
    print("✅ Importação do app bem-sucedida")
except Exception as e:
    print(f"❌ Erro na importação: {e}")
    import traceback
    traceback.print_exc()
