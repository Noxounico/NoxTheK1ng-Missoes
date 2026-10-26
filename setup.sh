#!/bin/bash

echo "🔧 Discord Bot Setup"
echo "===================="

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não está instalado"
    exit 1
fi

echo "✅ Python encontrado: $(python3 --version)"

# Create venv
echo ""
echo "📦 Criando ambiente virtual..."
python3 -m venv venv

# Activate venv
source venv/bin/activate || . venv/Scripts/activate

# Install deps
echo "📥 Instalando dependências..."
pip install -r requirements.txt

# Copy .env
if [ ! -f .env ]; then
    echo ""
    echo "⚠️  Arquivo .env não encontrado"
    echo "📋 Copiando .env.example → .env"
    cp .env.example .env
    echo "📝 Edita .env com teu DISCORD_TOKEN"
fi

echo ""
echo "✅ Setup completo!"
echo ""
echo "Para rodar localmente:"
echo "  source venv/bin/activate  (Linux/Mac)"
echo "  venv\\Scripts\\activate   (Windows)"
echo "  python bot_safe.py"
echo ""
echo "Para Railway:"
echo "  git add . && git commit -m 'Ready to deploy'"
echo "  git push origin main"
