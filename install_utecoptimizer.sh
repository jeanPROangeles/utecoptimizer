#!/bin/bash

echo "🛠️ Instalador de UtecOptimizer por Jean"

# === Configuración ===
REPO_URL="https://github.com/jeanPROangeles/utecoptimizer.git"
WORKDIR="$HOME/utecoptimizer_tmp"
ALIAS_NAME="utecopt"
TARGET_PATH="/usr/local/bin/$ALIAS_NAME"

# === Preparación ===
echo "📁 Creando carpeta temporal: $WORKDIR"
rm -rf "$WORKDIR"
mkdir -p "$WORKDIR"
cd "$WORKDIR" || exit 1

# === Clonar repo ===
echo "📥 Clonando desde $REPO_URL..."
git clone "$REPO_URL"
cd utecoptimizer || { echo "❌ No se pudo acceder al proyecto"; exit 1; }

# === Preparar ejecutable ===
echo "🔧 Haciendo ejecutable el script Python..."
chmod +x main.py

# === Crear comando global ===
echo "🔗 Enlazando como comando global: $ALIAS_NAME"
sudo ln -sf "$(pwd)/main.py" "$TARGET_PATH"

# === Verificación ===
echo ""
if command -v $ALIAS_NAME &>/dev/null; then
    echo "✅ Instalación exitosa"
    echo "Puedes usarlo con:  $ALIAS_NAME archivo.txt"
    echo "→ Generará: archivo.s"
else
    echo "❌ Algo salió mal. ¿Tienes permisos sudo?"
    exit 1
fi

echo ""
echo "🧹 Puedes eliminar $WORKDIR si ya no lo necesitas"
