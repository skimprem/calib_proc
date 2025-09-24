#!/bin/bash

# Скрипт для генерации документации в различных форматах
# Использование: ./generate_docs.sh

echo "🚀 Генерация документации Calibration Processing..."

# Проверяем наличие pandoc
if ! command -v pandoc &> /dev/null; then
    echo "❌ Pandoc не найден. Установите: sudo apt install pandoc"
    exit 1
fi

# Основные переменные
CSS="style.css"
AUTHOR="Roman Sermiagin"
DATE="$(date '+%Y-%m-%d')"

# Функция для генерации документов
generate_docs() {
    local input_file="$1"
    local title="$2"
    local base_name="${input_file%.md}"
    
    echo "📄 Генерируем HTML версию для $input_file..."
    pandoc "$input_file" \
        -s \
        --css="$CSS" \
        --toc \
        --toc-depth=3 \
        --metadata title="$title" \
        --metadata author="$AUTHOR" \
        --metadata date="$DATE" \
        -o "${base_name}.html"

    echo "📝 Генерируем Word версию для $input_file..."
    pandoc "$input_file" \
        --toc \
        --toc-depth=3 \
        --metadata title="$title" \
        --metadata author="$AUTHOR" \
        --metadata date="$DATE" \
        -o "${base_name}.docx"

    echo "🌐 Генерируем самодостаточный HTML для $input_file..."
    pandoc "$input_file" \
        -s \
        --embed-resources \
        --standalone \
        --css="$CSS" \
        --toc \
        --toc-depth=3 \
        --metadata title="$title" \
        --metadata author="$AUTHOR" \
        --metadata date="$DATE" \
        -o "${base_name}_standalone.html"
}

# Генерируем документацию для всех файлов
if [ -f "tutorial.md" ]; then
    generate_docs "tutorial.md" "Calibration Processing Tutorial"
fi

if [ -f "examples.md" ]; then
    generate_docs "examples.md" "Calibration Processing Examples"
fi

if [ -f "quick-guide.md" ]; then
    generate_docs "quick-guide.md" "Calibration Processing Quick Guide"
fi

echo ""
echo "✅ Генерация документации завершена!"
echo "   Созданы HTML и DOCX версии для всех найденных файлов Markdown."
echo ""
echo "💡 Рекомендации:"
echo "   • Для просмотра: откройте .html файлы в браузере"
echo "   • Для печати: используйте _standalone.html версии"
echo "   • Для редактирования: используйте .docx файлы"
echo ""
echo "🎉 Готово!"