import os
import sys
from pathlib import Path
from PIL import Image

# ================= НАСТРОЙКИ =================
# Папка для входных изображений (создаётся рядом со скриптом)
INPUT_DIR = "in"
# Папка для результатов
OUTPUT_DIR = "out"

# Режим работы: "pillow" (простой, по цвету) или "rembg" (AI, для сложных фонов)
MODE = "pillow"  

# Параметры для режима "pillow":
# Пиксели, у которых все каналы (R, G, B) >= этого значения, считаются фоном.
# Для белого фона подходит 240. Для светло-серого можно снизить до 200–220.
THRESHOLD = 220  
# ============================================

def remove_bg_pillow(img: Image.Image) -> Image.Image:
    """Удаляет белый/серый фон, делая его прозрачным (простой метод)."""
    img = img.convert("RGBA")
    datas = img.getdata()
    new_data = []
    for item in datas:
        # Если все цветовые каналы >= THRESHOLD, считаем пиксель фоном
        if item[0] >= THRESHOLD and item[1] >= THRESHOLD and item[2] >= THRESHOLD:
            # Полностью прозрачный пиксель
            new_data.append((255, 255, 255, 0))
        else:
            new_data.append(item)
    img.putdata(new_data)
    return img

def remove_bg_rembg(input_path: Path, output_path: Path):
    """Удаляет фон с помощью AI-библиотеки rembg (для сложных случаев)."""
    try:
        from rembg import remove
        from PIL import Image
        import io
    except ImportError:
        print("❌ Для режима 'rembg' установите библиотеку: pip install rembg")
        sys.exit(1)

    with open(input_path, "rb") as f:
        input_data = f.read()

    output_data = remove(input_data)
    output_image = Image.open(io.BytesIO(output_data))
    output_image.save(output_path, "PNG")

def main():
    # Определяем пути относительно расположения скрипта
    script_dir = Path(__file__).parent.resolve()
    in_path = script_dir / INPUT_DIR
    out_path = script_dir / OUTPUT_DIR

    # Проверяем наличие папки in
    if not in_path.exists():
        print(f"❌ Папка '{INPUT_DIR}' не найдена рядом со скриптом: {script_dir}")
        print("   Создайте её и поместите туда изображения.")
        sys.exit(1)

    # Создаём папку out, если её нет
    out_path.mkdir(exist_ok=True)

    # Поддерживаемые расширения
    valid_exts = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tiff", ".tif"}
    files = [f for f in in_path.iterdir() if f.suffix.lower() in valid_exts and f.is_file()]

    if not files:
        print(f"⚠️ В папке '{INPUT_DIR}' не найдено изображений.")
        return

    print(f"📁 Найдено {len(files)} изображений. Режим: {MODE}")

    for file_path in files:
        out_file = out_path / f"{file_path.stem}.png"
        print(f"   → {file_path.name}  ->  {out_file.name}")

        try:
            if MODE == "pillow":
                with Image.open(file_path) as img:
                    result = remove_bg_pillow(img)
                    result.save(out_file, "PNG")
            elif MODE == "rembg":
                remove_bg_rembg(file_path, out_file)
            else:
                print(f"❌ Неизвестный режим: {MODE}")
                sys.exit(1)
        except Exception as e:
            print(f"   ❌ Ошибка при обработке {file_path.name}: {e}")

    print(f"\n✅ Готово! Результаты в папке: {out_path}")

if __name__ == "__main__":
    main()