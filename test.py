import os

import qrcode


qr_data = f"https://epower.xiaojukeji.com/epower/static/resources/xcxconf/XIAOJU.101437000.001224000200060507"

# 创建二维码
qr = qrcode.QRCode(
    version=8,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=15,
    border=2,
)
qr.add_data(qr_data)
qr.make(fit=True)

# 生成二维码图片
img = qr.make_image(fill='black', back_color='white')

# 保存二维码图片
img_path = os.path.join("C:\Works\XIAOJU", f'枪07.png')
img.save(img_path)
