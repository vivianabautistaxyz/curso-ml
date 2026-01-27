#!/bin/bash

# Script para configurar usuario de Git para este repositorio

echo "🔧 Configuración de Git para este repositorio"
echo "=========================================="
echo ""

# Mostrar configuración actual
echo "📋 Configuración actual:"
echo "Nombre: $(git config user.name 2>/dev/null || echo 'No configurado')"
echo "Email: $(git config user.email 2>/dev/null || echo 'No configurado')"
echo ""

# Preguntar si desea cambiar la configuración
read -p "¿Deseas configurar/cambiar el usuario de Git? (s/n): " respuesta

if [[ $respuesta =~ ^[Ss]$ ]]; then
    echo ""
    
    # Pedir nombre de usuario
    read -p "👤 Ingresa tu nombre de usuario de GitHub: " nombre
    
    # Pedir email
    read -p "📧 Ingresa tu email de GitHub: " email
    
    echo ""
    
    # Confirmar configuración
    echo "✅ Configuración que se aplicará:"
    echo "Nombre: $nombre"
    echo "Email: $email"
    echo ""
    
    read -p "¿Confirmar configuración? (s/n): " confirmar
    
    if [[ $confirmar =~ ^[Ss]$ ]]; then
        # Aplicar configuración local (solo para este repositorio)
        git config user.name "$nombre"
        git config user.email "$email"
        
        echo ""
        echo "✅ ¡Configuración aplicada con éxito!"
        echo ""
        
        # Mostrar nueva configuración
        echo "📋 Nueva configuración:"
        echo "Nombre: $(git config user.name)"
        echo "Email: $(git config user.email)"
        echo ""
        echo "🎯 Esta configuración aplica solo a este repositorio."
        echo "   Para configurar globalmente, usa: git config --global"
        
    else
        echo "❌ Configuración cancelada."
    fi
    
else
    echo "❌ No se realizarán cambios."
fi

echo ""
echo "🏁 Script finalizado."
