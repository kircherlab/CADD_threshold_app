from PIL import Image
img = Image.open("Website/www/IconCADDThresholdAnalysis.png")
# produce multiple sizes inside the .ico
img.save("Website/www/favicon.ico", sizes=[(16,16), (32,32), (48,48), (64,64)])
print("wrote www/favicon.ico")
