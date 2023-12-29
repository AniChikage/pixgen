from PIL import Image, ImageFilter

# 打开第一个图片
image1_path = "1211_1.jpg"
image1 = Image.open(image1_path)

# 打开第二个图片（带有透明度）
image2_path = "1211_1_removebg_YyWq6KkD.png"
image2 = Image.open(image2_path)

print(image1.size)
print(image2.size)

# 确保两张图片的尺寸相同
if image1.size != image2.size:
    image1 = image1.resize(image2.size)

# 高斯模糊第一个图片
blurred_image1 = image1.filter(ImageFilter.GaussianBlur(radius=10))  # 调整radius以控制模糊程度

# 将第二个图片合并到第一个图片上
result_image = Image.alpha_composite(blurred_image1.convert("RGBA"), image2.convert("RGBA"))

# 保存合并后的图片
result_image.save("test.png", format="PNG")

# 显示合并后的图片
# result_image.show()
