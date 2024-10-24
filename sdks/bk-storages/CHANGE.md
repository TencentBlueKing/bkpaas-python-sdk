## Change logs

### 2.0.0

- 支持 Python 3.11，移除对 Python 3.6, 3.7 的支持
- Django 版本要求 >= 3.2.25
- 禁止在保存的文件名中使用绝对路径（如：/etc/passwd）或相对路径（如：../../passwd）

### 1.1.1

- 扩展支持的 Python 版本（>=3.6,<3.12)

### 1.1.0
 
- 调整 `BKRepoStorage` 公开仓库的 url 实现: 直接返回资源的路径, 而并非生成临时访问地址

### 1.0.8
 
- 扩展支持的 Python 版本（>=3.6,<3.11), 并修复单元测试在 django>=2.2.27 时无法通过的问题

### 1.0.7
 
- 修复 `BKRepoStorage` 在保存没有配置名称的 File 对象时会触发无法上传的问题

### 1.0.6

- `BKRepoStorage` 增加 DownloadFailedError 和 UploadFailedError 异常

### 1.0.5

- `BKRepoStorage` 增加访问 bkrepo 服务的超时机制

### 1.0.4

- 修复 `BKRepoStorage` 的 get_modified_time 返回的数据未正确处理的问题

### 1.0.3

- `BKRepoStorage` 模块增加错误重试机制

### 1.0.2

- 修复 `BKRepoStorage` 的 file_overwrite 不生效的问题

### 1.0.1

- 修复 `storage.url`，并修改目录名

### 1.0.0

- 删除 cos 与 legacy 子模块
