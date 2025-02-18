import requests

# 访问 Flask 服务器的 /backup 端点
response = requests.post("http://127.0.0.1:5001/backup")

if response.status_code == 200:
    print("✅ 备份成功！")
else:
    print(f"❌ 备份失败，HTTP 状态码：{response.status_code}")
    print("🔎 API 返回：", response.text)
