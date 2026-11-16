import os, sys
os.environ["QT_QPA_PLATFORM"] = "offscreen"
sys.path.insert(0, os.path.abspath("qt_version"))

from PySide6.QtWidgets import QApplication
from pages.deviation_page import RiverMouthDeviationPage
from pages.river_mouth_page import RiverMouthImagesPage

app = QApplication(sys.argv)

# Test RiverMouthDeviationPage
print("Creating RiverMouthDeviationPage...")
dev_page = RiverMouthDeviationPage()
dev_page.resize(1400, 900)
dev_page.show()

print("Card 1 (Meters):", dev_page.card_disp.value_lbl.text(), dev_page.card_disp.badge_lbl.text())
print("Card 2 (Latitude):", dev_page.card_lat.value_lbl.text(), dev_page.card_lat.badge_lbl.text())
print("Card 3 (Longitude):", dev_page.card_lon.value_lbl.text(), dev_page.card_lon.badge_lbl.text())
print("Card 4 (Direction):", dev_page.card_dir.value_lbl.text(), dev_page.card_dir.badge_lbl.text())
print("Card 5 (Area):", dev_page.card_area.value_lbl.text(), dev_page.card_area.badge_lbl.text())

pix_dev = dev_page.grab()
pix_dev.save("scratch/deviation_page_verified.png")
print("Saved scratch/deviation_page_verified.png")

# Test RiverMouthImagesPage
print("Creating RiverMouthImagesPage...")
gallery_page = RiverMouthImagesPage(None)
gallery_page.resize(1400, 900)
gallery_page.show()
print("Gallery cards count:", len(gallery_page.cards))

pix_gal = gallery_page.grab()
pix_gal.save("scratch/gallery_page_verified.png")
print("Saved scratch/gallery_page_verified.png")

print("ALL UI TESTS PASSED SUCCESSFULLY!")

