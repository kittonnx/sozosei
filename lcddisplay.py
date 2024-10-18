import smbus
import time
import sys

# LCDの設定
LCD_ADDR = 0x27  # LCDのI2Cアドレス
LCD_WIDTH = 16  # LCDの文字数
LCD_BACKLIGHT = 0x08  # バックライトの設定

# HD44780コマンド
LCD_CLEAR_DISPLAY = 0x01
LCD_RETURN_HOME = 0x02
LCD_ENTRY_MODE = 0x06
LCD_DISPLAY_ON = 0x0C
LCD_DISPLAY_OFF = 0x08
LCD_CURSOR_ON = 0x0E
LCD_BLINK_ON = 0x0F
LCD_SET_DDRAM = 0x80

# PCF8574に接続されたLCDのピン
RS = 0x01
RW = 0x02
EN = 0x04

# LCDの初期化
def lcd_init(bus):
    # 初期化シーケンス
    lcd_send(bus, 0x33, 0)  # 4ビットモードに設定
    time.sleep(0.005)
    lcd_send(bus, 0x32, 0)  # 4ビットモードに設定
    time.sleep(0.005)

    # コマンド設定
    lcd_send(bus, 0x28, 0)  # 2行表示、5x8ドット
    time.sleep(0.00015)
    lcd_send(bus, LCD_DISPLAY_OFF, 0)  # ディスプレイオフ
    time.sleep(0.00015)
    lcd_send(bus, LCD_CLEAR_DISPLAY, 0)  # ディスプレイクリア
    time.sleep(0.002)
    lcd_send(bus, LCD_ENTRY_MODE, 0)  # エントリモード設定
    time.sleep(0.00015)
    lcd_send(bus, LCD_DISPLAY_ON, 0)  # ディスプレイオン
    time.sleep(0.00015)

# データ送信
def lcd_send(bus, data, mode):
    high = mode | (data & 0xF0) | LCD_BACKLIGHT  # 上位4ビット
    low = mode | ((data << 4) & 0xF0) | LCD_BACKLIGHT  # 下位4ビット

    # データを送信
    bus.write_byte(LCD_ADDR, high)
    lcd_toggle_enable(bus, high)
    bus.write_byte(LCD_ADDR, low)
    lcd_toggle_enable(bus, low)

# トグル処理
def lcd_toggle_enable(bus, value):
    bus.write_byte(LCD_ADDR, value | EN)  # Enable ON
    time.sleep(0.0005)
    bus.write_byte(LCD_ADDR, value & ~EN)  # Enable OFF
    time.sleep(0.0005)

# カーソル位置設定
def lcd_set_cursor(bus, col, row):
    addr = LCD_SET_DDRAM | (col + 0x40 * row)
    lcd_send(bus, addr, 0)

# 文字列出力
def lcd_print(bus, text):
    for char in text:
        lcd_send(bus, ord(char), 1)

# メイン処理
def main():
    args = sys.argv
    bus = smbus.SMBus(1)
    lcd_init(bus)

    # 文字列を表示
    text_line1 = args[0]
    text_line2 = args[1]

    lcd_set_cursor(bus, 0, 0)
    lcd_print(bus, text_line1)

    lcd_set_cursor(bus, 0, 1)
    lcd_print(bus, text_line2)

    time.sleep(10)  # 10秒間表示を維持
    lcd_send(bus, LCD_CLEAR_DISPLAY, 1)  # 表示をクリア

if __name__ == "__main__":
    main()