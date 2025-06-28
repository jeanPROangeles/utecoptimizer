#!/bin/bash

echo "🛠️ Instalador de UtecOptimizer por Jean"

# === Configuración ===
REPO_URL="https://github.com/jeanPROangeles/utecoptimizer.git"
WORKDIR="$HOME/utecoptimizer_tmp"
ALIAS_NAME="utecopt"
TARGET_PATH="/usr/local/bin/$ALIAS_NAME"

# === Preparación ===
echo "📁 Creando carpeta temporal en: $WORKDIR"
rm -rf "$WORKDIR"
mkdir -p "$WORKDIR"
cd "$WORKDIR" || exit 1

# === Clonación del repositorio ===
echo "📥 Clonando repositorio desde GitHub..."
git clone "$REPO_URL"
cd utecoptimizer || { echo "❌ No se pudo entrar al proyecto"; exit 1; }

# === Permisos y enlace simbólico ===
echo "🔧 Configurando ejecutable..."
chmod +x main.py
sudo ln -sf "$(pwd)/main.py" "$TARGET_PATH"

# === Verificación ===
echo ""
if command -v $ALIAS_NAME &> /dev/null; then
    echo "✅ Instalación completada correctamente"
    echo "Puedes ejecutar tu optimizador así:"
    echo "  $ALIAS_NAME entrada.txt"
    echo "  → Generará salida: entrada.s"
else
    echo "❌ Falló la creación del comando global '$ALIAS_NAME'"
    echo "Verifica si tienes permisos de administrador"
    exit 1
fi

echo ""
echo "📌 Proyecto clonado en: $WORKDIR/utecoptimizer"
echo "🧹 Puedes eliminar esa carpeta cuando termines"
