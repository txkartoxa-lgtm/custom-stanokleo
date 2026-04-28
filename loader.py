import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import json

# Настройка темы
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class ConfigManager:
    """Менеджер конфигурации для сохранения настроек"""
    def __init__(self, config_path="config.json"):
        self.config_path = config_path
        self.config = self.load_config()
    
    def load_config(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "game_folder": "",
            "standalo_path": "",
            "fps_unlock": False,
            "fps_value": 60,
            "texture_quality": 100,
            "map_skin": ""
        }
    
    def save_config(self):
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=4, ensure_ascii=False)

class LoaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.config_manager = ConfigManager()
        
        # Настройки окна
        self.title("Game Loader by mellontyfan")
        self.geometry("900x600")
        self.minsize(800, 500)
        
        # Настройка сетки
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.create_sidebar()
        self.create_main_area()
        
        # Загрузка сохраненных значений
        self.load_saved_values()
    
    def create_sidebar(self):
        """Создание боковой панели с навигацией"""
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="ns")
        self.sidebar.grid_rowconfigure(6, weight=1)
        
        # Логотип/Название вверху слева
        self.logo_label = ctk.CTkLabel(
            self.sidebar, 
            text="by mellontyfan", 
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w"
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        
        # Кнопки навигации
        self.nav_buttons = {}
        nav_items = [
            ("Главная", "home"),
            ("Рескин карты", "map_skin"),
            ("Буст FPS", "fps_boost"),
            ("Анлок FPS", "fps_unlock"),
            ("Настройки", "settings")
        ]
        
        for i, (text, key) in enumerate(nav_items, start=1):
            btn = ctk.CTkButton(
                self.sidebar,
                text=text,
                command=lambda k=key: self.show_section(k),
                anchor="w",
                height=40
            )
            btn.grid(row=i, column=0, padx=10, pady=5, sticky="ew")
            self.nav_buttons[key] = btn
        
        # Выделить первую кнопку
        self.nav_buttons["home"].configure(fg_color="#3B8ED0")
    
    def create_main_area(self):
        """Создание основной области контента"""
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # Секции
        self.sections = {}
        self.create_home_section()
        self.create_map_skin_section()
        self.create_fps_boost_section()
        self.create_fps_unlock_section()
        self.create_settings_section()
        
        # Показать только главную секцию
        self.show_section("home")
    
    def create_home_section(self):
        """Главная секция"""
        frame = ctk.CTkFrame(self.main_frame)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.grid_columnconfigure(0, weight=1)
        
        # Путь к папке игры
        ctk.CTkLabel(frame, text="Путь к папке игры:", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=0, column=0, padx=20, pady=(30, 10), sticky="w"
        )
        
        self.game_folder_entry = ctk.CTkEntry(frame, height=40, font=ctk.CTkFont(size=12))
        self.game_folder_entry.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        
        self.game_browse_btn = ctk.CTkButton(
            frame, 
            text="Обзор...", 
            command=self.browse_game_folder,
            height=35
        )
        self.game_browse_btn.grid(row=1, column=1, padx=10, pady=10)
        
        # Путь к Standalo
        ctk.CTkLabel(frame, text="Путь к Standalo:", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=2, column=0, padx=20, pady=(20, 10), sticky="w"
        )
        
        self.standalo_entry = ctk.CTkEntry(frame, height=40, font=ctk.CTkFont(size=12))
        self.standalo_entry.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        
        self.standalo_browse_btn = ctk.CTkButton(
            frame, 
            text="Обзор...", 
            command=self.browse_standalo,
            height=35
        )
        self.standalo_browse_btn.grid(row=3, column=1, padx=10, pady=10)
        
        # Кнопка запуска
        self.launch_btn = ctk.CTkButton(
            frame,
            text="ЗАПУСТИТЬ",
            command=self.launch_game,
            height=50,
            font=ctk.CTkFont(size=18, weight="bold"),
            fg_color="#2CC985"
        )
        self.launch_btn.grid(row=4, column=0, columnspan=2, padx=20, pady=40, sticky="ew")
        
        self.sections["home"] = frame
    
    def create_map_skin_section(self):
        """Секция рескина карты"""
        frame = ctk.CTkFrame(self.main_frame)
        
        ctk.CTkLabel(frame, text="Рескин карты", font=ctk.CTkFont(size=20, weight="bold")).pack(
            padx=20, pady=(30, 20)
        )
        
        ctk.CTkLabel(
            frame, 
            text="Выберите текстуру для карты:",
            font=ctk.CTkFont(size=14)
        ).pack(padx=20, pady=10)
        
        self.map_skin_var = ctk.StringVar(value="Стандартная")
        skin_options = ["Стандартная", "Зима", "Ночь", "Пустыня", "Киберпанк", "Своя..."]
        
        self.skin_segmented = ctk.CTkSegmentedButton(
            frame,
            values=skin_options,
            variable=self.map_skin_var,
            command=self.on_map_skin_change
        )
        self.skin_segmented.pack(padx=20, pady=20)
        
        self.custom_skin_entry = ctk.CTkEntry(frame, placeholder_text="Путь к своей текстуре...")
        self.custom_skin_entry.pack(padx=20, pady=10, fill="x")
        self.custom_skin_entry.pack_forget()  # Скрыто по умолчанию
        
        self.map_skin_preview = ctk.CTkLabel(
            frame,
            text="Предпросмотр: Стандартная",
            font=ctk.CTkFont(size=12)
        )
        self.map_skin_preview.pack(padx=20, pady=20)
        
        self.sections["map_skin"] = frame
    
    def create_fps_boost_section(self):
        """Секция буста FPS"""
        frame = ctk.CTkFrame(self.main_frame)
        
        ctk.CTkLabel(frame, text="Буст FPS", font=ctk.CTkFont(size=20, weight="bold")).pack(
            padx=20, pady=(30, 20)
        )
        
        ctk.CTkLabel(
            frame, 
            text="Понижение качества текстур:",
            font=ctk.CTkFont(size=14)
        ).pack(padx=20, pady=10)
        
        self.texture_quality_var = ctk.IntVar(value=100)
        self.texture_slider = ctk.CTkSlider(
            frame,
            from_=0,
            to=100,
            number_of_steps=20,
            variable=self.texture_quality_var,
            command=self.on_texture_change,
            width=400
        )
        self.texture_slider.pack(padx=20, pady=20)
        
        self.texture_label = ctk.CTkLabel(
            frame,
            text="Качество текстур: 100%",
            font=ctk.CTkFont(size=16)
        )
        self.texture_label.pack(padx=20, pady=10)
        
        ctk.CTkLabel(
            frame,
            text="⚠️ Чем меньше значение, тем ниже качество и выше FPS",
            font=ctk.CTkFont(size=11),
            text_color="#FFA500"
        ).pack(padx=20, pady=10)
        
        self.sections["fps_boost"] = frame
    
    def create_fps_unlock_section(self):
        """Секция анлока FPS"""
        frame = ctk.CTkFrame(self.main_frame)
        
        ctk.CTkLabel(frame, text="Анлок FPS", font=ctk.CTkFont(size=20, weight="bold")).pack(
            padx=20, pady=(30, 20)
        )
        
        self.fps_unlock_var = ctk.BooleanVar(value=False)
        self.fps_unlock_switch = ctk.CTkSwitch(
            frame,
            text="Включить анлок FPS",
            variable=self.fps_unlock_var,
            command=self.on_fps_unlock_toggle,
            font=ctk.CTkFont(size=14)
        )
        self.fps_unlock_switch.pack(padx=20, pady=20)
        
        ctk.CTkLabel(
            frame,
            text="Установить лимит FPS (1-999):",
            font=ctk.CTkFont(size=14)
        ).pack(padx=20, pady=10)
        
        self.fps_value_var = ctk.IntVar(value=60)
        self.fps_spinbox = ctk.CTkSpinBox(
            frame,
            from_=1,
            to=999,
            width=150,
            font=ctk.CTkFont(size=16),
            variable=self.fps_value_var,
            command=self.on_fps_value_change
        )
        self.fps_spinbox.set(60)
        self.fps_spinbox.pack(padx=20, pady=10)
        
        self.fps_status_label = ctk.CTkLabel(
            frame,
            text="Статус: Выключено",
            font=ctk.CTkFont(size=14),
            text_color="#FF6B6B"
        )
        self.fps_status_label.pack(padx=20, pady=20)
        
        self.sections["fps_unlock"] = frame
    
    def create_settings_section(self):
        """Секция настроек"""
        frame = ctk.CTkFrame(self.main_frame)
        
        ctk.CTkLabel(frame, text="Настройки", font=ctk.CTkFont(size=20, weight="bold")).pack(
            padx=20, pady=(30, 20)
        )
        
        ctk.CTkLabel(
            frame,
            text="Сохранение конфигурации",
            font=ctk.CTkFont(size=14)
        ).pack(padx=20, pady=20)
        
        self.save_config_btn = ctk.CTkButton(
            frame,
            text="Сохранить настройки",
            command=self.save_all_settings,
            height=40
        )
        self.save_config_btn.pack(padx=20, pady=10)
        
        self.reset_config_btn = ctk.CTkButton(
            frame,
            text="Сбросить настройки",
            command=self.reset_settings,
            fg_color="#FF6B6B",
            height=40
        )
        self.reset_config_btn.pack(padx=20, pady=10)
        
        info_text = """
Информация о программе:
- Версия: 1.0
- Автор: mellontyfan
- Назначение: Загрузчик с модификациями

Функции:
✓ Рескин карты
✓ Буст FPS (понижение текстур)
✓ Анлок FPS (1-999)
✓ Сохранение настроек
        """
        
        info_label = ctk.CTkLabel(
            frame,
            text=info_text,
            font=ctk.CTkFont(size=11),
            justify="left"
        )
        info_label.pack(padx=20, pady=30)
        
        self.sections["settings"] = frame
    
    def show_section(self, section_name):
        """Показать выбранную секцию"""
        # Скрыть все секции
        for section in self.sections.values():
            section.grid_forget()
        
        # Сбросить стиль кнопок
        for btn in self.nav_buttons.values():
            btn.configure(fg_color="transparent", hover_color="#2B2B2B")
        
        # Показать выбранную секцию
        self.sections[section_name].grid(row=0, column=0, sticky="nsew")
        self.nav_buttons[section_name].configure(fg_color="#3B8ED0")
    
    def browse_game_folder(self):
        """Выбор папки игры"""
        folder = filedialog.askdirectory(title="Выберите папку с игрой")
        if folder:
            self.game_folder_entry.delete(0, 'end')
            self.game_folder_entry.insert(0, folder)
    
    def browse_standalo(self):
        """Выбор файла Standalo"""
        file = filedialog.askopenfilename(
            title="Выберите файл Standalo",
            filetypes=[("Executable files", "*.exe"), ("All files", "*.*")]
        )
        if file:
            self.standalo_entry.delete(0, 'end')
            self.standalo_entry.insert(0, file)
    
    def on_map_skin_change(self, value):
        """Изменение скина карты"""
        if value == "Своя...":
            self.custom_skin_entry.pack(padx=20, pady=10, fill="x")
            self.map_skin_preview.configure(text="Предпросмотр: Своя текстура")
        else:
            self.custom_skin_entry.pack_forget()
            self.map_skin_preview.configure(text=f"Предпросмотр: {value}")
    
    def on_texture_change(self, value):
        """Изменение качества текстур"""
        quality = int(float(value))
        self.texture_quality_var.set(quality)
        self.texture_label.configure(text=f"Качество текстур: {quality}%")
    
    def on_fps_unlock_toggle(self):
        """Переключение анлока FPS"""
        if self.fps_unlock_var.get():
            self.fps_status_label.configure(
                text="Статус: Включено",
                text_color="#2CC985"
            )
        else:
            self.fps_status_label.configure(
                text="Статус: Выключено",
                text_color="#FF6B6B"
            )
    
    def on_fps_value_change(self, value):
        """Изменение значения FPS"""
        self.fps_value_var.set(int(value))
    
    def load_saved_values(self):
        """Загрузка сохраненных значений"""
        config = self.config_manager.config
        
        if config.get("game_folder"):
            self.game_folder_entry.delete(0, 'end')
            self.game_folder_entry.insert(0, config["game_folder"])
        
        if config.get("standalo_path"):
            self.standalo_entry.delete(0, 'end')
            self.standalo_entry.insert(0, config["standalo_path"])
        
        if config.get("map_skin"):
            self.map_skin_var.set(config["map_skin"])
        
        if config.get("texture_quality"):
            self.texture_slider.set(config["texture_quality"])
            self.texture_label.configure(text=f"Качество текстур: {config['texture_quality']}%")
        
        if config.get("fps_unlock"):
            self.fps_unlock_var.set(config["fps_unlock"])
            self.fps_status_label.configure(
                text="Статус: Включено",
                text_color="#2CC985"
            )
        
        if config.get("fps_value"):
            self.fps_spinbox.set(config["fps_value"])
    
    def save_all_settings(self):
        """Сохранение всех настроек"""
        config = {
            "game_folder": self.game_folder_entry.get(),
            "standalo_path": self.standalo_entry.get(),
            "map_skin": self.map_skin_var.get(),
            "texture_quality": self.texture_quality_var.get(),
            "fps_unlock": self.fps_unlock_var.get(),
            "fps_value": self.fps_value_var.get()
        }
        
        self.config_manager.config = config
        self.config_manager.save_config()
        
        messagebox.showinfo("Успешно", "Настройки сохранены!")
    
    def reset_settings(self):
        """Сброс настроек"""
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите сбросить все настройки?"):
            self.game_folder_entry.delete(0, 'end')
            self.standalo_entry.delete(0, 'end')
            self.map_skin_var.set("Стандартная")
            self.texture_slider.set(100)
            self.texture_label.configure(text="Качество текстур: 100%")
            self.fps_unlock_var.set(False)
            self.fps_spinbox.set(60)
            self.fps_status_label.configure(
                text="Статус: Выключено",
                text_color="#FF6B6B"
            )
            
            self.config_manager.config = self.config_manager.load_config()
            self.config_manager.save_config()
    
    def launch_game(self):
        """Запуск игры"""
        game_folder = self.game_folder_entry.get()
        standalo_path = self.standalo_entry.get()
        
        if not game_folder:
            messagebox.showwarning("Предупреждение", "Укажите путь к папке игры!")
            return
        
        if not standalo_path:
            messagebox.showwarning("Предупреждение", "Укажите путь к Standalo!")
            return
        
        if not os.path.exists(game_folder):
            messagebox.showerror("Ошибка", "Папка игры не найдена!")
            return
        
        if not os.path.exists(standalo_path):
            messagebox.showerror("Ошибка", "Файл Standalo не найден!")
            return
        
        # Сохраняем настройки перед запуском
        self.save_all_settings()
        
        # Здесь должна быть логика применения модификаций
        # и запуска игры
        messagebox.showinfo(
            "Готово к запуску",
            f"Настройки применены:\n\n"
            f"📁 Папка игры: {game_folder}\n"
            f"🎮 Standalo: {standalo_path}\n"
            f"🗺️ Скин карты: {self.map_skin_var.get()}\n"
            f"📊 Качество текстур: {self.texture_quality_var.get()}%\n"
            f"⚡ Анлок FPS: {'Вкл' if self.fps_unlock_var.get() else 'Выкл'}\n"
            f"🎯 Лимит FPS: {self.fps_value_var.get()}\n\n"
            f"by mellontyfan"
        )

if __name__ == "__main__":
    app = LoaderApp()
    app.mainloop()
