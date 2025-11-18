# Node.js 路径配置说明

## Windows 环境变量配置文件位置

### 1. 系统环境变量（所有用户）

**注册表位置：**
```
HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Session Manager\Environment
```

**配置文件：**
- 通过系统属性配置：`控制面板` → `系统` → `高级系统设置` → `环境变量`
- 系统变量中的 `Path` 变量

### 2. 用户环境变量（当前用户）

**注册表位置：**
```
HKEY_CURRENT_USER\Environment
```

**配置文件：**
- 通过系统属性配置：`控制面板` → `系统` → `高级系统设置` → `环境变量`
- 用户变量中的 `Path` 变量

## 当前系统配置检查

### 系统 PATH 中的 Node.js 路径
根据检查，系统 PATH 中包含：
- `F:\nodejs\` （系统级配置）

### 检查该路径是否存在
请运行以下命令检查：
```powershell
Test-Path "F:\nodejs\node.exe"
```

如果返回 `True`，说明 Node.js 已安装在该位置，但可能：
1. 需要刷新环境变量
2. 需要重新打开终端
3. 路径配置有问题

## 如何修改 PATH 环境变量

### 方法一：通过图形界面（推荐）

1. **打开环境变量设置**
   - 按 `Win + R`，输入 `sysdm.cpl`，回车
   - 或：`控制面板` → `系统` → `高级系统设置`
   - 点击 `环境变量` 按钮

2. **编辑 PATH 变量**
   - 在 `系统变量` 或 `用户变量` 中找到 `Path`
   - 点击 `编辑`
   - 检查是否包含 Node.js 路径（如 `F:\nodejs\`）
   - 如果不存在，点击 `新建` 添加 Node.js 安装目录

3. **保存并重启终端**
   - 点击 `确定` 保存所有更改
   - **重要**：关闭所有终端窗口，重新打开才能生效

### 方法二：通过 PowerShell（管理员权限）

```powershell
# 查看当前用户 PATH
[Environment]::GetEnvironmentVariable("Path", "User")

# 添加 Node.js 路径到用户 PATH（示例）
$nodePath = "F:\nodejs"
$currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($currentPath -notlike "*$nodePath*") {
    $newPath = "$currentPath;$nodePath"
    [Environment]::SetEnvironmentVariable("Path", $newPath, "User")
    Write-Host "已添加 $nodePath 到用户 PATH" -ForegroundColor Green
}

# 刷新当前会话的 PATH
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
```

### 方法三：通过注册表（高级用户）

1. 按 `Win + R`，输入 `regedit`，回车
2. 导航到：
   - 系统变量：`HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Session Manager\Environment`
   - 用户变量：`HKEY_CURRENT_USER\Environment`
3. 找到 `Path` 值，编辑添加 Node.js 路径

## 验证配置

配置完成后，**重新打开 PowerShell**，运行：

```powershell
# 检查 Node.js
node --version

# 检查 npm
npm --version

# 检查 Node.js 路径
where.exe node

# 检查 npm 路径
where.exe npm
```

## 常见问题

### 问题 1：路径已添加但仍无法识别

**解决方案：**
1. 确认路径正确（包含 `node.exe`）
2. 关闭所有终端窗口
3. 重新打开终端
4. 如果仍不行，重启计算机

### 问题 2：多个 Node.js 版本冲突

**解决方案：**
- 只保留一个 Node.js 安装路径在 PATH 中
- 推荐使用 Node.js 官方安装程序，会自动配置 PATH

### 问题 3：PATH 中有无效路径

**解决方案：**
- 检查 PATH 中所有路径是否存在
- 删除不存在的路径
- 清理 PATH 中的重复项

## 项目特定配置

### 本项目不需要特殊配置

本项目使用系统全局的 Node.js 和 npm，不需要在项目内配置路径。

### 如果需要在项目中指定 Node.js 路径

可以在 `启动前端.bat` 中指定完整路径：

```batch
@echo off
cd /d "%~dp0"
set NODE_PATH=F:\nodejs
set PATH=%NODE_PATH%;%PATH%
npm run dev
```

## 推荐做法

1. **使用官方安装程序**
   - 从 https://nodejs.org/ 下载安装
   - 安装时勾选 "Add to PATH"

2. **使用 Node Version Manager (nvm-windows)**
   - 可以管理多个 Node.js 版本
   - 下载：https://github.com/coreybutler/nvm-windows

3. **验证安装**
   - 安装后立即验证
   - 确保 `node` 和 `npm` 命令可用

## 快速检查脚本

创建 `检查Node.js.bat`：

```batch
@echo off
echo 检查 Node.js 配置...
echo.

where.exe node >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] node 命令可用
    node --version
) else (
    echo [错误] node 命令不可用
)

where.exe npm >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] npm 命令可用
    npm --version
) else (
    echo [错误] npm 命令不可用
)

echo.
echo PATH 中的 Node.js 相关路径:
echo %PATH% | findstr /i "node"
pause
```

