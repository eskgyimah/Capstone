"""
PNG Banner Generator for Capstone Presentation
Converts HTML banner to high-quality PNG image
"""

import os
import sys

def create_banner_png_method1():
    """
    Method 1: Using weasyprint (recommended)
    Install: pip install weasyprint
    """
    try:
        from weasyprint import HTML

        html_file = 'presentation_banner.html'
        output_file = 'presentation_banner.png'

        print("Creating PNG using WeasyPrint...")
        HTML(filename=html_file).write_png(output_file, resolution=300)
        print(f"✅ PNG created successfully: {output_file}")
        return True
    except ImportError:
        print("❌ WeasyPrint not installed. Install with: pip install weasyprint")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def create_banner_png_method2():
    """
    Method 2: Using selenium with Chrome
    Install: pip install selenium pillow
    Requires: Chrome browser and chromedriver
    """
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from PIL import Image
        import time

        html_file = os.path.abspath('presentation_banner.html')
        output_file = 'presentation_banner.png'

        print("Creating PNG using Selenium + Chrome...")

        # Configure Chrome
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1400,800')

        # Start browser
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(f'file:///{html_file}')
        time.sleep(2)

        # Take screenshot
        driver.save_screenshot(output_file)
        driver.quit()

        print(f"✅ PNG created successfully: {output_file}")
        return True
    except ImportError:
        print("❌ Selenium or Pillow not installed. Install with: pip install selenium pillow")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def create_banner_png_method3():
    """
    Method 3: Using html2image
    Install: pip install html2image
    """
    try:
        from html2image import Html2Image

        html_file = 'presentation_banner.html'
        output_file = 'presentation_banner'

        print("Creating PNG using html2image...")

        hti = Html2Image(output_path='.', size=(1200, 400))

        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()

        hti.screenshot(html_str=html_content, save_as=f'{output_file}.png')

        print(f"✅ PNG created successfully: {output_file}.png")
        return True
    except ImportError:
        print("❌ html2image not installed. Install with: pip install html2image")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def manual_instructions():
    """Print manual screenshot instructions"""
    print("\n" + "="*70)
    print("📸 MANUAL METHOD - Create PNG Screenshot")
    print("="*70)
    print("\n1. Open 'presentation_banner.html' in your web browser")
    print("2. Use one of these methods to capture:")
    print("\n   WINDOWS:")
    print("   • Press: Windows + Shift + S")
    print("   • Select the banner area")
    print("   • Paste into Paint and save as PNG")
    print("\n   MAC:")
    print("   • Press: Cmd + Shift + 4")
    print("   • Drag to select banner area")
    print("   • File saved to Desktop automatically")
    print("\n   BROWSER (Chrome/Edge):")
    print("   • Press F12 (Open DevTools)")
    print("   • Press Ctrl+Shift+P (Command Palette)")
    print("   • Type: 'screenshot'")
    print("   • Select: 'Capture node screenshot'")
    print("   • Click on banner element")
    print("\n3. Save as: presentation_banner.png")
    print("="*70 + "\n")

def main():
    """Try multiple methods to create PNG"""
    print("\n" + "="*70)
    print("🎨 CAPSTONE PRESENTATION BANNER - PNG GENERATOR")
    print("="*70 + "\n")

    # Change to script directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Try methods in order of preference
    methods = [
        ("Method 1: WeasyPrint", create_banner_png_method1),
        ("Method 2: Selenium", create_banner_png_method2),
        ("Method 3: html2image", create_banner_png_method3),
    ]

    success = False
    for method_name, method_func in methods:
        print(f"\nTrying {method_name}...")
        if method_func():
            success = True
            break
        print()

    if not success:
        print("\n⚠️  Automated methods failed. Please use manual method:\n")
        manual_instructions()
        print("\n💡 TIP: Install required libraries:")
        print("   pip install weasyprint")
        print("   pip install selenium pillow")
        print("   pip install html2image")
    else:
        print("\n✅ Banner PNG created successfully!")
        print("📁 Location: presentation_banner.png")
        print("\n📊 Specifications:")
        print("   • Size: 1200 x 400 pixels")
        print("   • Format: PNG with transparency support")
        print("   • Resolution: High-quality (300 DPI)")
        print("   • Ready for presentations, websites, and print")

if __name__ == "__main__":
    main()
