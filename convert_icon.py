import sys
from PIL import Image

if len(sys.argv) != 2:
    print("Usage: python convert_icon.py <input_image>")
    sys.exit(1)

input_path = sys.argv[1]
output_path = "icon.ico"

try:
    img = Image.open(input_path)
    # Сохраняем как ICO с несколькими размерами для лучшей совместимости
    img.save(output_path, format='ICO', sizes=[(16,16),(32,32),(48,48),(64,64),(128,128),(256,256)])
    print("✅ Иконка успешно сконвертирована в icon.ico")
except Exception as e:
    print(f"❌ Ошибка конвертации: {e}", file=sys.stderr)
    sys.exit(1)
