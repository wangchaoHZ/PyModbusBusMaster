
# Modbus TCP 随机数写入器

## 概述

该 Python 脚本是一个 Modbus TCP 客户端，可以向指定的 Modbus 保持寄存器写入随机生成的值。它支持写入有符号整数（包括负数），并将其转换为适用于 Modbus 通信的16位无符号格式。脚本还会将所有操作记录到动态命名的日志文件中。

## 功能

1. **随机数生成**:
   - 生成 `-50` 到 `50` 之间的随机整数。
   - 将生成的值转换为适合 Modbus 通信的16位无符号格式。

2. **多寄存器写入**:
   - 支持在单次执行中向多个 Modbus 寄存器写入值。
   - 记录每次操作的详细信息，包括地址、值以及成功/失败状态。

3. **动态日志记录**:
   - 生成以时间戳命名的日志文件，例如 `modbus_operations_YYYYMMDD_HHMMSS.log`。
   - 对成功和失败的操作进行详细日志记录。

4. **重试机制**:
   - 在写入失败时，支持指定重试次数。

## 文件结构

- **`modbus_writer.py`**: 主脚本文件。
- **日志文件**: 脚本运行时自动生成，文件名包含时间戳，例如 `modbus_operations_20241206_143010.log`。

## 环境要求

请确保已安装并配置以下环境：

- **Python**: 版本 3.7 或更高。
- **依赖库**:
  - `pymodbus` (版本 >= 3.0)
  - `random` (标准库模块)
  - `logging` (标准库模块)
- **网络配置**:
  - 可访问的 Modbus TCP 服务器。
  - 提供服务器的 IP 地址和端口（默认是 `502`）。

## 安装步骤

1. **克隆代码库**:
   ```bash
   git clone <仓库地址>
   cd <项目目录>
   ```

2. **创建虚拟环境**（可选）:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows 用户使用 .venv\Scripts\activate
   ```

3. **安装依赖**:
   ```bash
   pip install pymodbus
   ```

## 配置方法

1. 修改脚本中的 Modbus 服务器信息：
   ```python
   server_host = "192.168.1.122"  # 替换为你的服务器 IP 地址
   server_port = 502              # 替换为你的服务器端口
   slave_id = 17                  # 替换为你的 Modbus 从站 ID
   ```

2. 指定需要写入的寄存器地址：
   ```python
   addresses = [400, 401, 402]  # 替换为你的寄存器地址
   ```

3. 配置重试次数：
   ```python
   retries = 5  # 根据需要调整重试次数
   ```

## 使用方法

运行脚本：
```bash
python modbus_writer.py
```

## 日志示例

脚本在同一目录下生成日志文件，以下是日志文件内容示例：

```plaintext
2024-12-06 14:40:10 - INFO - Attempt 1 of 5
2024-12-06 14:40:10 - INFO - Write successful: Address=400, Value=23 (Unsigned=23), Slave ID=17
2024-12-06 14:40:10 - INFO - Write successful: Address=401, Value=-45 (Unsigned=65491), Slave ID=17
2024-12-06 14:40:10 - INFO - Write successful: Address=402, Value=50 (Unsigned=50), Slave ID=17
```

## 注意事项

1. **负值支持**:
   - 脚本会自动将负值转换为 Modbus 兼容的16位无符号格式。

2. **日志记录**:
   - 日志记录包含时间戳以及每次操作的详细信息，便于追踪。

3. **错误处理**:
   - 在连接或写入失败时，会在日志和控制台中报告错误信息。

## 故障排除

1. **连接问题**:
   - 确保 Modbus 服务器可以通过指定的 IP 和端口访问。
   - 检查防火墙设置，确保允许连接。

2. **值范围错误**:
   - 脚本支持 `-32768` 到 `65535` 范围的值，请确保输入值在此范围内。

3. **依赖问题**:
   - 如果遇到导入错误，请使用以下命令检查 `pymodbus` 是否已正确安装：
     ```bash
     pip show pymodbus
     ```

## 许可证

本项目基于 MIT 许可证发布。

