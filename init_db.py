from app import app, db
from models import Product, Brand, User, CartItem, Favorite, Order, OrderItem, PCBuild
from flask_bcrypt import Bcrypt
from sqlalchemy import text
import json

bcrypt = Bcrypt()

def seed():
    with app.app_context():
        # Удаляем все таблицы и создаем заново
        print("Пересоздание базы данных...")
        db.drop_all()
        db.create_all()
        
        print("Таблицы созданы заново.")

        # Create test user
        test_user = User(
            username='test_user',
            email='test@example.com',
            password=bcrypt.generate_password_hash('password123').decode('utf-8')
        )
        db.session.add(test_user)
        db.session.flush()

        # Products by category with detailed specs
        categories = {
            "Смартфоны": [
                {"name": "Samsung Galaxy S23", "price": 79999.99, "specs": "Snapdragon 8 Gen 2, 8GB RAM, 256GB"},
                {"name": "iPhone 15 Pro", "price": 99999.99, "specs": "A17 Pro, 8GB RAM, 256GB"},
                {"name": "Xiaomi Redmi Note 12", "price": 19999.99, "specs": "Snapdragon 685, 6GB RAM, 128GB"},
                {"name": "Google Pixel 8", "price": 69999.99, "specs": "Tensor G3, 8GB RAM, 128GB"},
                {"name": "OnePlus 11", "price": 54999.99, "specs": "Snapdragon 8 Gen 2, 16GB RAM, 256GB"},
                {"name": "Huawei P60 Pro", "price": 64999.99, "specs": "Snapdragon 8+ Gen 1, 8GB RAM, 256GB"},
                {"name": "Sony Xperia 1 V", "price": 74999.99, "specs": "Snapdragon 8 Gen 2, 12GB RAM, 256GB"},
                {"name": "Nothing Phone 2", "price": 44999.99, "specs": "Snapdragon 8+ Gen 1, 12GB RAM, 256GB"},
            ],
            "Ноутбуки": [
                {"name": "MacBook Air M2", "price": 109999.99, "specs": "Apple M2, 8GB RAM, 256GB SSD"},
                {"name": "Dell XPS 15", "price": 89999.99, "specs": "Intel i7-13700H, 16GB RAM, 512GB SSD"},
                {"name": "Lenovo ThinkPad X1", "price": 79999.99, "specs": "Intel i7-1365U, 16GB RAM, 512GB SSD"},
                {"name": "ASUS ROG Zephyrus", "price": 129999.99, "specs": "RTX 4070, 32GB RAM, 1TB SSD"},
                {"name": "Acer Swift 3", "price": 49999.99, "specs": "Intel i5-1240P, 8GB RAM, 512GB SSD"},
                {"name": "HP Spectre x360", "price": 89999.99, "specs": "Intel i7-1355U, 16GB RAM, 512GB SSD"},
                {"name": "MSI Stealth 15M", "price": 99999.99, "specs": "RTX 4060, 16GB RAM, 512GB SSD"},
                {"name": "Huawei MateBook D16", "price": 59999.99, "specs": "Intel i5-12450H, 16GB RAM, 512GB SSD"},
            ],
            "Видеокарты": [
                {"name": "NVIDIA RTX 4090", "price": 159999.99, "specs": "24GB GDDR6X, DLSS 3.0"},
                {"name": "RTX 4080", "price": 109999.99, "specs": "16GB GDDR6X, DLSS 3.0"},
                {"name": "RTX 4070 Ti", "price": 79999.99, "specs": "12GB GDDR6X, DLSS 3.0"},
                {"name": "RTX 4060 Ti", "price": 44999.99, "specs": "8GB GDDR6, DLSS 3.0"},
                {"name": "AMD RX 7900 XTX", "price": 89999.99, "specs": "24GB GDDR6, FSR 3.0"},
                {"name": "AMD RX 7800 XT", "price": 54999.99, "specs": "16GB GDDR6, FSR 3.0"},
                {"name": "Intel Arc A770", "price": 34999.99, "specs": "16GB GDDR6, XeSS"},
                {"name": "NVIDIA RTX 3060", "price": 29999.99, "specs": "12GB GDDR6, DLSS 2.0"},
            ],
            "Процессоры": [
                {"name": "Intel Core i9-13900K", "price": 59999.99, "specs": "24 ядра, 5.8 GHz"},
                {"name": "AMD Ryzen 9 7950X", "price": 54999.99, "specs": "16 ядер, 5.7 GHz"},
                {"name": "Intel Core i7-13700K", "price": 39999.99, "specs": "16 ядер, 5.4 GHz"},
                {"name": "AMD Ryzen 7 7800X3D", "price": 44999.99, "specs": "8 ядер, 5.0 GHz, 3D V-Cache"},
                {"name": "Intel Core i5-13600K", "price": 29999.99, "specs": "14 ядер, 5.1 GHz"},
                {"name": "AMD Ryzen 5 7600X", "price": 22999.99, "specs": "6 ядер, 5.3 GHz"},
                {"name": "Intel Core i3-13100", "price": 13999.99, "specs": "4 ядра, 4.5 GHz"},
                {"name": "AMD Ryzen 3 4100", "price": 8999.99, "specs": "4 ядра, 4.0 GHz"},
            ],
            "Материнские платы": [
                {"name": "ASUS ROG STRIX Z790", "price": 29999.99, "specs": "LGA1700, DDR5, PCIe 5.0"},
                {"name": "MSI MAG B760M", "price": 14999.99, "specs": "LGA1700, DDR5, PCIe 4.0"},
                {"name": "Gigabyte Z790 AORUS", "price": 34999.99, "specs": "LGA1700, DDR5, WiFi 6E"},
                {"name": "ASRock B650E", "price": 19999.99, "specs": "AM5, DDR5, PCIe 5.0"},
                {"name": "MSI PRO B660M-A", "price": 11999.99, "specs": "LGA1700, DDR4, PCIe 4.0"},
                {"name": "ASUS TUF Gaming X670", "price": 27999.99, "specs": "AM5, DDR5, WiFi 6E"},
            ],
            "Оперативная память": [
                {"name": "Kingston Fury Beast DDR5 32GB", "price": 11999.99, "specs": "DDR5-5600, CL36"},
                {"name": "Corsair Vengeance DDR5 32GB", "price": 12999.99, "specs": "DDR5-6000, CL30"},
                {"name": "G.Skill Trident Z5 32GB", "price": 13999.99, "specs": "DDR5-6400, CL32"},
                {"name": "Crucial Ballistix DDR4 32GB", "price": 8999.99, "specs": "DDR4-3600, CL16"},
                {"name": "ADATA XPG Lancer 16GB", "price": 5999.99, "specs": "DDR5-5200, CL38"},
                {"name": "TeamGroup T-Force 16GB", "price": 4999.99, "specs": "DDR4-3200, CL16"},
            ],
            "Мониторы": [
                {"name": "Dell UltraSharp 27 4K", "price": 49999.99, "specs": "27\", 4K, IPS, 60Hz"},
                {"name": "LG 27GP950", "price": 59999.99, "specs": "27\", 4K, 144Hz, HDMI 2.1"},
                {"name": "Samsung Odyssey G7", "price": 44999.99, "specs": "27\", QHD, 240Hz, VA"},
                {"name": "ASUS TUF VG27AQ", "price": 34999.99, "specs": "27\", QHD, 165Hz, IPS"},
                {"name": "Acer Nitro XV272U", "price": 29999.99, "specs": "27\", QHD, 144Hz, IPS"},
                {"name": "BenQ PD2700U", "price": 39999.99, "specs": "27\", 4K, IPS, 60Hz, HDR"},
            ],
        }

        print("Добавление товаров...")
        product_id = 1
        for cat, products in categories.items():
            for i, prod in enumerate(products):
                img_url = f"https://picsum.photos/400/400?random={product_id}"
                product = Product(
                    name=prod["name"],
                    category=cat,
                    price=prod["price"],
                    image_url=img_url,
                    description=f"{prod['name']} - {prod['specs']}. Отличный выбор для современных задач. Высокое качество, надежность и производительность.",
                    specs=json.dumps({"specifications": prod["specs"]}),
                    stock=50 + i * 10
                )
                db.session.add(product)
                product_id += 1

        # Add more categories
        additional_categories = {
            "Вентиляторы": 8,
            "Электросамокаты": 5,
            "Мобильные кондиционеры": 5,
            "Триммеры бензиновые": 5,
            "Датчики": 8,
            "Освещение": 8,
            "Розетки": 6,
            "Выключатели": 6,
            "Центры управления": 4,
            "Леска для триммеров": 5,
        }

        for cat, count in additional_categories.items():
            for i in range(count):
                name = f"{cat} - Модель {i+1}"
                price = round(1999.99 + (i * 500), 2)
                product = Product(
                    name=name,
                    category=cat,
                    price=price,
                    image_url=f"https://picsum.photos/400/400?random={product_id}",
                    description=f"Отличный выбор: {name}. Современные характеристики, надежность и стильный дизайн.",
                    stock=20 + i * 5
                )
                db.session.add(product)
                product_id += 1

        # Brands with logos
        print("Добавление брендов...")
        brands = [
            Brand(name="Apple", logo_url="https://upload.wikimedia.org/wikipedia/commons/f/fa/Apple_logo_black.svg",
                  description="Американская корпорация, производитель персональных и планшетных компьютеров, аудиоплееров, телефонов, программного обеспечения."),
            Brand(name="Samsung", logo_url="https://upload.wikimedia.org/wikipedia/commons/2/24/Samsung_Logo.svg",
                  description="Южнокорейская группа компаний, один из крупнейших чеболей, производитель электроники."),
            Brand(name="Xiaomi", logo_url="https://upload.wikimedia.org/wikipedia/commons/a/ae/Xiaomi_logo_%282021-%29.svg",
                  description="Китайская компания, производитель электроники и умных устройств."),
            Brand(name="LG", logo_url="https://upload.wikimedia.org/wikipedia/commons/b/bf/LG_logo_%282015%29.svg",
                  description="Южнокорейская компания, производитель электроники и бытовой техники."),
            Brand(name="ASUS", logo_url="https://upload.wikimedia.org/wikipedia/commons/2/28/Asus-Logo.svg",
                  description="Тайваньская компания, производитель компьютерной техники и комплектующих."),
            Brand(name="MSI", logo_url="https://upload.wikimedia.org/wikipedia/commons/1/1e/MSI_Logo_2012.png",
                  description="Тайваньская компания, производитель компьютерных комплектующих и ноутбуков."),
            Brand(name="Intel", logo_url="https://upload.wikimedia.org/wikipedia/commons/7/7d/Intel_logo_%282006-2020%29.svg",
                  description="Американская компания, крупнейший производитель процессоров."),
            Brand(name="AMD", logo_url="https://upload.wikimedia.org/wikipedia/commons/7/7c/AMD_Logo.svg",
                  description="Американская компания, производитель процессоров и видеокарт."),
            Brand(name="NVIDIA", logo_url="https://upload.wikimedia.org/wikipedia/commons/2/21/Nvidia_logo.svg",
                  description="Американская компания, лидер в производстве графических процессоров."),
            Brand(name="Dell", logo_url="https://upload.wikimedia.org/wikipedia/commons/1/18/Dell_logo_2016.svg",
                  description="Американская компания, производитель компьютеров и серверного оборудования."),
            Brand(name="HP", logo_url="https://upload.wikimedia.org/wikipedia/commons/a/ad/HP_logo_2012.svg",
                  description="Американская компания, производитель компьютеров и периферийного оборудования."),
            Brand(name="Lenovo", logo_url="https://upload.wikimedia.org/wikipedia/commons/b/b8/Lenovo_logo_2015.svg",
                  description="Китайская компания, крупнейший производитель персональных компьютеров."),
        ]
        
        for b in brands:
            db.session.add(b)

        db.session.commit()
        
        print("=" * 50)
        print("✅ База данных успешно заполнена!")
        print(f"📦 Создано товаров: {Product.query.count()}")
        print(f"🏷️ Создано брендов: {Brand.query.count()}")
        print(f"👤 Тестовый пользователь: test@example.com")
        print(f"🔑 Пароль: password123")
        print("=" * 50)
        print("\n🚀 Теперь можете запустить приложение: python app.py")

if __name__ == "__main__":
    seed()