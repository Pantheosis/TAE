from PIL import Image

# app_icon_source.png is a 2048px reduction of the owner's 4096px master
# (abbasid-astrology-icon-master-4096.png, kept outside the repo); nothing
# below needs more than the 1024px .icns slot.
img = Image.open("app_icon_source.png")
icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
img.save("app_icon.ico", format="ICO", sizes=icon_sizes)

# .icns for the macOS .app bundle (build.spec's BUNDLE(icon=...)). Pillow
# downsamples the full-res source to fill every size Apple expects, up to
# the 1024px (@2x) slot.
img.convert("RGBA").save("app_icon.icns", format="ICNS")
