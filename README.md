# Gradio局域网代理工具

一个简单的代理工具，用于将本地Gradio服务暴露到局域网中。专门为 [biliTickerBuy](https://github.com/mikumifa/biliTickerBuy) 项目设计，但也适用于其他基于Gradio的Web应用。

> 本项目只能给普通用户在手机上监看使用！黄牛使用4000+！

## 特性

- 🚀 自动扫描并发现本地Gradio服务（端口范围：7860-7960）
- 🔒 支持多IP网段访问控制
- 🌐 支持多端口同时代理
- 💻 简单易用的命令行界面
- 🎨 彩色日志输出
- ⚡ 快速启动，低资源占用

## 快速开始

### 方法一：直接运行

1. 下载最新的发布版本
2. 解压后直接运行 `portProxy.exe`

### 方法二：从源码运行

1. 克隆仓库
```bash
git clone https://github.com/Mapleawaa/biliTickerBuyProxy.git
```

2. 安装依赖
```bash
pip install colorama
```

3. 运行程序
```bash
python portProxy.py
```

## 配置说明

首次运行时会在`proxy`文件夹下生成`config.json`配置文件：

```json
{
    "allowed_networks": ["192.168.1."],
    "port_range": {
        "start": 7860,
        "end": 7961
    },
    "buffer_size": 4096
}
```

- `allowed_networks`: 允许访问的IP网段列表
- `port_range`: Gradio服务端口扫描范围
- `buffer_size`: 数据传输缓冲区大小

## 使用场景

1. 在运行biliTickerBuy等Gradio应用时，默认只允许本机访问
2. 使用本工具可以让局域网内的其他设备访问这些服务
3. 支持多个Gradio服务同时代理

## 注意事项

1. 仅支持局域网内访问，不建议暴露到公网(HTTP协议并不安全！)
2. 确保防火墙允许相应端口的访问
3. 建议在使用完毕后关闭程序（Ctrl+C）

## 特别鸣谢

- [biliTickerBuy](https://github.com/mikumifa/biliTickerBuy) - B站会员购抢票工具
- [Trae IDE](https://www.trae.ai/) - AI辅助编程工具

## 许可证

MIT License

        