#include <windows.h>
#include <commctrl.h>
#include <shlobj.h>
#include <string>
#include <fstream>
#include <sstream>
#include <iomanip>

#pragma comment(lib, "comctl32.lib")
#pragma comment(lib, "shell32.lib")
#pragma comment(lib, "gdi32.lib")
#pragma comment(lib, "user32.lib")

// Глобальные переменные для хранения настроек
std::string gamePath = "";
std::string standaloPath = "";
int textureQuality = 50; // 0-100
int fpsLimit = 60;
bool unlockFps = false;
int selectedSkin = 0; // 0-Standard, 1-Winter, etc.

// Контролы
HWND hEditGamePath, hEditStandaloPath;
HWND hTrackTexture, hTrackFps;
HWND hCheckUnlockFps;
HWND hComboSkin;
HWND hStaticFpsValue, hStaticTextureValue;
HWND hTabCtrl;

const char* CONFIG_FILE = "loader_config.ini";

// Функции для работы с файлами
void LoadConfig() {
    std::ifstream file(CONFIG_FILE);
    if (file.is_open()) {
        std::string line;
        while (std::getline(file, line)) {
            if (line.find("gamePath=") == 0) gamePath = line.substr(9);
            else if (line.find("standaloPath=") == 0) standaloPath = line.substr(13);
            else if (line.find("textureQuality=") == 0) textureQuality = std::stoi(line.substr(15));
            else if (line.find("fpsLimit=") == 0) fpsLimit = std::stoi(line.substr(9));
            else if (line.find("unlockFps=") == 0) unlockFps = (line.substr(10) == "1");
            else if (line.find("selectedSkin=") == 0) selectedSkin = std::stoi(line.substr(13));
        }
        file.close();
    }
}

void SaveConfig() {
    std::ofstream file(CONFIG_FILE);
    if (file.is_open()) {
        file << "gamePath=" << gamePath << "\n";
        file << "standaloPath=" << standaloPath << "\n";
        file << "textureQuality=" << textureQuality << "\n";
        file << "fpsLimit=" << fpsLimit << "\n";
        file << "unlockFps=" << (unlockFps ? "1" : "0") << "\n";
        file << "selectedSkin=" << selectedSkin << "\n";
        file.close();
    }
}

// Диалог выбора папки
std::string BrowseFolder(HWND hwnd) {
    BROWSEINFO bi = { 0 };
    bi.lpszTitle = "Выберите папку";
    bi.ulFlags = BIF_RETURNONLYFSDIRS | BIF_NEWDIALOGSTYLE;
    
    LPITEMIDLIST pidl = SHBrowseForFolder(&bi);
    if (pidl != 0) {
        char path[MAX_PATH];
        SHGetPathFromIDList(pidl, path);
        IMalloc* imalloc = 0;
        if (SUCCEEDED(SHGetMalloc(&imalloc))) {
            imalloc->Free(pidl);
            imalloc->Release();
        }
        return std::string(path);
    }
    return "";
}

// Обработчик сообщений
LRESULT CALLBACK WndProc(HWND hwnd, UINT msg, WPARAM wParam, LPARAM lParam) {
    switch (msg) {
        case WM_CREATE: {
            // Инициализация контролов
            LoadConfig();

            // Лейбл "by mellontyfan" слева вверху
            CreateWindowEx(0, "STATIC", "by mellontyfan", 
                WS_CHILD | WS_VISIBLE | SS_LEFT, 
                10, 10, 150, 20, hwnd, NULL, NULL, NULL);

            // Кнопка выбора пути к игре
            CreateWindowEx(0, "BUTTON", "Путь к папке игры:", 
                WS_CHILD | WS_VISIBLE | BS_LEFT, 
                20, 50, 200, 25, hwnd, NULL, NULL, NULL);
            
            hEditGamePath = CreateWindowEx(WS_EX_CLIENTEDGE, "EDIT", gamePath.c_str(), 
                WS_CHILD | WS_VISIBLE | ES_AUTOHSCROLL, 
                20, 80, 300, 25, hwnd, NULL, NULL, NULL);

            CreateWindowEx(0, "BUTTON", "Обзор...", 
                WS_CHILD | WS_VISIBLE | BS_PUSHBUTTON, 
                330, 80, 70, 25, hwnd, (HMENU)101, NULL, NULL);

            // Кнопка выбора пути к Standalo
            CreateWindowEx(0, "BUTTON", "Путь к Standalo:", 
                WS_CHILD | WS_VISIBLE | BS_LEFT, 
                20, 120, 200, 25, hwnd, NULL, NULL, NULL);
            
            hEditStandaloPath = CreateWindowEx(WS_EX_CLIENTEDGE, "EDIT", standaloPath.c_str(), 
                WS_CHILD | WS_VISIBLE | ES_AUTOHSCROLL, 
                20, 150, 300, 25, hwnd, NULL, NULL, NULL);

            CreateWindowEx(0, "BUTTON", "Обзор...", 
                WS_CHILD | WS_VISIBLE | BS_PUSHBUTTON, 
                330, 150, 70, 25, hwnd, (HMENU)102, NULL, NULL);

            // Разделитель
            CreateWindowEx(0, "BUTTON", "", 
                WS_CHILD | WS_VISIBLE | BS_GROUPBOX, 
                10, 190, 400, 250, hwnd, NULL, NULL, NULL);
            CreateWindowEx(0, "STATIC", "Настройки графики и FPS", 
                WS_CHILD | WS_VISIBLE | SS_CENTER, 
                20, 200, 380, 20, hwnd, NULL, NULL, NULL);

            // Рескин карты (ComboBox)
            CreateWindowEx(0, "STATIC", "Рескин карты:", 
                WS_CHILD | WS_VISIBLE, 
                30, 230, 100, 20, hwnd, NULL, NULL, NULL);
            
            hComboSkin = CreateWindowEx(0, "COMBOBOX", "", 
                WS_CHILD | WS_VISIBLE | CBS_DROPDOWNLIST | WS_VSCROLL, 
                30, 255, 150, 100, hwnd, (HMENU)103, NULL, NULL);
            
            SendMessage(hComboSkin, CB_ADDSTRING, 0, (LPARAM)"Стандартная");
            SendMessage(hComboSkin, CB_ADDSTRING, 0, (LPARAM)"Зима");
            SendMessage(hComboSkin, CB_ADDSTRING, 0, (LPARAM)"Ночь");
            SendMessage(hComboSkin, CB_ADDSTRING, 0, (LPARAM)"Пустыня");
            SendMessage(hComboSkin, CB_ADDSTRING, 0, (LPARAM)"Киберпанк");
            SendMessage(hComboSkin, CB_SETCURSEL, selectedSkin, 0);

            // Буст FPS (Trackbar)
            CreateWindowEx(0, "STATIC", "Качество текстур (Буст FPS):", 
                WS_CHILD | WS_VISIBLE, 
                220, 230, 200, 20, hwnd, NULL, NULL, NULL);
            
            hStaticTextureValue = CreateWindowEx(0, "STATIC", std::to_string(textureQuality).c_str(), 
                WS_CHILD | WS_VISIBLE | SS_CENTER, 
                350, 230, 40, 20, hwnd, NULL, NULL, NULL);

            hTrackTexture = CreateWindowEx(0, TRACKBAR_CLASS, "", 
                WS_CHILD | WS_VISIBLE | TBS_AUTOTICKS | TBS_TOOLTIPS, 
                220, 255, 170, 30, hwnd, (HMENU)104, NULL, NULL);
            
            SendMessage(hTrackTexture, TBM_SETRANGEMIN, 0, 0);
            SendMessage(hTrackTexture, TBM_SETRANGEMAX, 0, 100);
            SendMessage(hTrackTexture, TBM_SETPOS, TRUE, textureQuality);

            // Анлок FPS
            hCheckUnlockFps = CreateWindowEx(0, "BUTTON", "Включить Анлок FPS", 
                WS_CHILD | WS_VISIBLE | BS_AUTOCHECKBOX, 
                30, 300, 150, 25, hwnd, (HMENU)105, NULL, NULL);
            
            if (unlockFps) SendMessage(hCheckUnlockFps, BM_SETCHECK, BST_CHECKED, 0);

            CreateWindowEx(0, "STATIC", "Лимит FPS (1-999):", 
                WS_CHILD | WS_VISIBLE, 
                30, 330, 150, 20, hwnd, NULL, NULL, NULL);

            hStaticFpsValue = CreateWindowEx(0, "STATIC", std::to_string(fpsLimit).c_str(), 
                WS_CHILD | WS_VISIBLE | SS_CENTER, 
                160, 330, 40, 20, hwnd, NULL, NULL, NULL);

            hTrackFps = CreateWindowEx(0, TRACKBAR_CLASS, "", 
                WS_CHILD | WS_VISIBLE | TBS_AUTOTICKS | TBS_TOOLTIPS, 
                30, 355, 200, 30, hwnd, (HMENU)106, NULL, NULL);
            
            SendMessage(hTrackFps, TBM_SETRANGEMIN, 0, 1);
            SendMessage(hTrackFps, TBM_SETRANGEMAX, 0, 999);
            SendMessage(hTrackFps, TBM_SETPOS, TRUE, fpsLimit);

            // Кнопка ЗАПУСТИТЬ
            HWND hBtnLaunch = CreateWindowEx(0, "BUTTON", "ЗАПУСТИТЬ ИГРУ", 
                WS_CHILD | WS_VISIBLE | BS_DEFPUSHBUTTON, 
                120, 400, 180, 40, hwnd, (HMENU)107, NULL, NULL);
            
            // Увеличим шрифт кнопки запуска
            HFONT hFont = CreateFont(16, 0, 0, 0, FW_BOLD, FALSE, FALSE, FALSE, 
                DEFAULT_CHARSET, OUT_DEFAULT_PRECIS, CLIP_DEFAULT_PRECIS, 
                DEFAULT_QUALITY, DEFAULT_PITCH | FF_DONTCARE, "Arial");
            SendMessage(hBtnLaunch, WM_SETFONT, (WPARAM)hFont, TRUE);

            break;
        }

        case WM_COMMAND: {
            int wmId = LOWORD(wParam);
            switch (wmId) {
                case 101: { // Обзор игра
                    std::string path = BrowseFolder(hwnd);
                    if (!path.empty()) {
                        gamePath = path;
                        SetWindowText(hEditGamePath, gamePath.c_str());
                    }
                    break;
                }
                case 102: { // Обзор standalo
                    std::string path = BrowseFolder(hwnd);
                    if (!path.empty()) {
                        standaloPath = path;
                        SetWindowText(hEditStandaloPath, standaloPath.c_str());
                    }
                    break;
                }
                case 107: { // Запуск
                    SaveConfig();
                    
                    // Здесь логика запуска
                    // В реальном проекте тут был бы CreateProcess или ShellExecuteEx
                    // Для демонстрации покажем сообщение
                    
                    std::string msg = "Конфигурация сохранена!\n";
                    msg += "Папка игры: " + gamePath + "\n";
                    msg += "Standalo: " + standaloPath + "\n";
                    msg += "Текстуры: " + std::to_string(textureQuality) + "%\n";
                    msg += "FPS Limit: " + std::to_string(fpsLimit) + "\n";
                    msg += "Unlock FPS: " + std::string(unlockFps ? "ON" : "OFF") + "\n";
                    
                    MessageBox(hwnd, msg.c_str(), "Запуск...", MB_ICONINFORMATION | MB_OK);
                    
                    // Пример реального запуска (раскомментировать при наличии путей)
                    /*
                    if (!standaloPath.empty()) {
                        ShellExecute(NULL, "open", (standaloPath + "\\game.exe").c_str(), NULL, NULL, SW_SHOWNORMAL);
                    }
                    */
                    break;
                }
            }
            break;
        }

        case WM_HSCROLL: {
            HWND hSlider = (HWND)lParam;
            if (hSlider == hTrackTexture) {
                int pos = SendMessage(hTrackTexture, TBM_GETPOS, 0, 0);
                textureQuality = pos;
                SetWindowText(hStaticTextureValue, std::to_string(pos).c_str());
            } else if (hSlider == hTrackFps) {
                int pos = SendMessage(hTrackFps, TBM_GETPOS, 0, 0);
                fpsLimit = pos;
                SetWindowText(hStaticFpsValue, std::to_string(pos).c_str());
            }
            break;
        }

        case WM_NOTIFY: {
            NMHDR* pNMHDR = (NMHDR*)lParam;
            if (pNMHDR->code == CBN_SELCHANGE && pNMHDR->hwndFrom == hComboSkin) {
                selectedSkin = SendMessage(hComboSkin, CB_GETCURSEL, 0, 0);
            }
            break;
        }
        
        case WM_CLOSE:
            SaveConfig();
            DestroyWindow(hwnd);
            break;

        case WM_DESTROY:
            PostQuitMessage(0);
            break;

        default:
            return DefWindowProc(hwnd, msg, wParam, lParam);
    }
    return 0;
}

int WINAPI WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, LPSTR lpCmdLine, int nCmdShow) {
    // Инициализация общих элементов управления (для Trackbar и ComboBox)
    INITCOMMONCONTROLSEX icex;
    icex.dwSize = sizeof(INITCOMMONCONTROLSEX);
    icex.dwICC = ICC_BAR_CLASSES | ICC_STANDARD_CLASSES;
    InitCommonControlsEx(&icex);

    const char CLASS_NAME[] = "GameLoaderClass";

    WNDCLASS wc = {};
    wc.lpfnWndProc = WndProc;
    wc.hInstance = hInstance;
    wc.lpszClassName = CLASS_NAME;
    wc.hCursor = LoadCursor(NULL, IDC_ARROW);
    wc.hbrBackground = (HBRUSH)(COLOR_WINDOW+1);
    wc.hIcon = LoadIcon(NULL, IDI_APPLICATION);

    RegisterClass(&wc);

    HWND hwnd = CreateWindowEx(
        0,
        CLASS_NAME,
        "Game Loader by mellontyfan",
        WS_OVERLAPPEDWINDOW & ~WS_THICKFRAME & ~WS_MAXIMIZEBOX,
        CW_USEDEFAULT, CW_USEDEFAULT, 450, 500,
        NULL,
        NULL,
        hInstance,
        NULL
    );

    if (hwnd == NULL) {
        return 0;
    }

    ShowWindow(hwnd, nCmdShow);
    UpdateWindow(hwnd);

    MSG msg = {};
    while (GetMessage(&msg, NULL, 0, 0)) {
        TranslateMessage(&msg);
        DispatchMessage(&msg);
    }

    return 0;
}
