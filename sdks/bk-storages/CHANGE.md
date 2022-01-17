## Change logs

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
