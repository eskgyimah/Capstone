"""
Large Poster PNG Generator - 48" x 60"
Creates high-resolution poster for printing
"""

import os

def create_poster_png_highres():
    """
    Create 48" x 60" poster at 300 DPI
    Size: 14,400 x 18,000 pixels (very large!)
    """
    try:
        from html2image import Html2Image

        html_file = 'presentation_banner_v2_poster.html'
        output_file = 'presentation_poster_48x60'

        print("Creating HIGH-RESOLUTION 48\"x60\" poster at 300 DPI...")
        print("⚠️  Warning: This will create a VERY LARGE file (~200-500 MB)")
        print("   Size: 14,400 x 18,000 pixels")

        response = input("\nContinue? (yes/no): ")
        if response.lower() not in ['yes', 'y']:
            print("Cancelled.")
            return False

        # 48" x 60" at 300 DPI
        width = 48 * 300  # 14,400 pixels
        height = 60 * 300  # 18,000 pixels

        hti = Html2Image(output_path='.', size=(width, height))

        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()

        print(f"\nGenerating {width} x {height} pixel image...")
        print("This may take several minutes...")

        hti.screenshot(html_str=html_content, save_as=f'{output_file}_300dpi.png')

        print(f"\n✅ HIGH-RES PNG created successfully!")
        print(f"📁 File: {output_file}_300dpi.png")
        print(f"📏 Size: {width} x {height} pixels (48\" x 60\" at 300 DPI)")
        print(f"💾 Ready for professional printing!")
        return True

    except ImportError:
        print("❌ html2image not installed.")
        print("   Install with: pip install html2image")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def create_poster_png_medium():
    """
    Create 48" x 60" poster at 150 DPI (more manageable size)
    Size: 7,200 x 9,000 pixels
    """
    try:
        from html2image import Html2Image

        html_file = 'presentation_banner_v2_poster.html'
        output_file = 'presentation_poster_48x60'

        print("Creating MEDIUM-RESOLUTION 48\"x60\" poster at 150 DPI...")
        print("Size: 7,200 x 9,000 pixels (good for most printing)")

        # 48" x 60" at 150 DPI
        width = 48 * 150  # 7,200 pixels
        height = 60 * 150  # 9,000 pixels

        hti = Html2Image(output_path='.', size=(width, height))

        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()

        print(f"\nGenerating {width} x {height} pixel image...")

        hti.screenshot(html_str=html_content, save_as=f'{output_file}_150dpi.png')

        print(f"\n✅ MEDIUM-RES PNG created successfully!")
        print(f"📁 File: {output_file}_150dpi.png")
        print(f"📏 Size: {width} x {height} pixels (48\" x 60\" at 150 DPI)")
        print(f"💾 Suitable for most printing applications")
        return True

    except ImportError:
        print("❌ html2image not installed.")
        print("   Install with: pip install html2image")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def create_poster_png_preview():
    """
    Create screen-size preview of poster
    Size: 960 x 1200 pixels (1/5 scale)
    """
    try:
        from html2image import Html2Image

        html_file = 'presentation_banner_v2_poster.html'
        output_file = 'presentation_poster_preview'

        print("Creating PREVIEW version of poster...")
        print("Size: 960 x 1200 pixels (for screen viewing)")

        width = 960
        height = 1200

        hti = Html2Image(output_path='.', size=(width, height))

        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()

        hti.screenshot(html_str=html_content, save_as=f'{output_file}.png')

        print(f"\n✅ PREVIEW PNG created successfully!")
        print(f"📁 File: {output_file}.png")
        print(f"📏 Size: {width} x {height} pixels")
        print(f"💻 Perfect for viewing on screen")
        return True

    except ImportError:
        print("❌ html2image not installed.")
        print("   Install with: pip install html2image")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def chrome_print_method():
    """Instructions for Chrome print method (most reliable)"""
    print("\n" + "="*70)
    print("🖨️  CHROME PRINT METHOD (RECOMMENDED FOR LARGE POSTERS)")
    print("="*70)
    print("\nThis method creates the best quality for large prints:")
    print("\n1. Open 'presentation_banner_v2_poster.html' in Google Chrome")
    print("\n2. Press Ctrl+P (or Cmd+P on Mac) to open Print dialog")
    print("\n3. Click 'More settings'")
    print("\n4. Set Paper size:")
    print("   • Click 'More...'")
    print("   • Width: 48 inches")
    print("   • Height: 60 inches")
    print("\n5. Set these options:")
    print("   • Destination: Save as PDF")
    print("   • Margins: None")
    print("   • Scale: 100%")
    print("   • Background graphics: ON")
    print("\n6. Click 'Save'")
    print("   • Save as: presentation_poster_48x60.pdf")
    print("\n7. Convert PDF to PNG:")
    print("   OPTION A: Use online converter")
    print("   • Go to: https://pdf2png.com")
    print("   • Upload PDF, select 300 DPI")
    print("   • Download PNG")
    print("\n   OPTION B: Use Photoshop/GIMP")
    print("   • Open PDF")
    print("   • Set resolution: 300 DPI")
    print("   • Export as PNG")
    print("\n   OPTION C: Use ImageMagick (command line)")
    print("   • Install ImageMagick")
    print("   • Run: magick -density 300 poster.pdf poster.png")
    print("\n8. Result: High-quality PNG ready for printing!")
    print("="*70 + "\n")

def main():
    """Main function with menu"""
    print("\n" + "="*70)
    print("🎨 CAPSTONE POSTER GENERATOR - 48\" x 60\"")
    print("="*70)

    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    print("\nChoose generation method:")
    print("\n1. Preview Size (960 x 1200 px) - Quick preview")
    print("2. Medium Resolution (7,200 x 9,000 px) - 150 DPI, good for printing")
    print("3. High Resolution (14,400 x 18,000 px) - 300 DPI, best quality")
    print("4. Chrome Print Method (RECOMMENDED) - Instructions")
    print("5. Exit")

    choice = input("\nEnter choice (1-5): ").strip()

    if choice == '1':
        create_poster_png_preview()
    elif choice == '2':
        create_poster_png_medium()
    elif choice == '3':
        create_poster_png_highres()
    elif choice == '4':
        chrome_print_method()
    elif choice == '5':
        print("Exiting...")
        return
    else:
        print("Invalid choice")

    print("\n" + "="*70)
    print("📊 POSTER SPECIFICATIONS")
    print("="*70)
    print("\nSize: 48 inches wide × 60 inches tall (portrait)")
    print("Recommended DPI: 150-300")
    print("Color Mode: RGB")
    print("Format: PNG (supports transparency)")
    print("\nPrinting Tips:")
    print("• Use a professional printing service for best results")
    print("• Request matte or semi-gloss finish")
    print("• Ensure printer supports 48×60 poster size")
    print("• Bring file on USB drive or email to print shop")
    print("\nEstimated Costs:")
    print("• Local print shop: $30-60")
    print("• Online services (Vistaprint, etc.): $40-80")
    print("• Campus printing (if available): $20-40")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
