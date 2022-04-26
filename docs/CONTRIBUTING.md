# Contributing to bkpaas-python-sdk

我们欢迎发起议题或者代码合并请求，在贡献之前请阅读以下指引。

## 问题管理
我们用 Github Issues 去跟踪产品缺陷和功能需求。

在发起新的议题之前，请查找已存在或者相类似的 issue，从而保证不存在冗余。

## 新建议题
新建议题时请提供详细的描述、截屏或者短视频来辅助我们定位问题，必要时请提供问题的复现方法，会让我们的协助定位更加及时准确。

## 分支管理
我们欢迎大家贡献代码来使 bkpaas-python-sdk 更加强大，代码团队会评审所有的合并请求, 同时进行代码检查和测试。

在发起合并请求前请做以下确认:

- 从 master 或者 hotfix fork 出你自己的开发分支。
- 在修改了代码之后请修改对应的文档和注释。
- 在新建的文件中请加入 license 和 copy right 申明。
- 确保一致的代码风格。
- 做充分的测试。 
  
然后，你可以提交你的代码到 dev 或者 hotfix 分支并发起合并请求。

## 开发相关

### 配置 pre-commit

本项目使用了 [pre-commit](https://pre-commit.com/) 工具来规范每个改动。在你提交代码前，请先安装 pre-commit
并执行 `pre-commit install` 安装钩子程序。

为了更方便的管理 pre-commit 所依赖的每个工具的版本，配置文件 `.pre-commit-config.yaml` 中的每个 hook（比如 `black`）
都选择了直接执行本地命令，而非默认的基于远程仓库来自动安装。因此，每次执行 `git commit` 前，请确保你已经激活了本项目的虚拟环境。

操作参考：

```console
$ cd {PATH}                 # 切换到项目根目录
$ pre-commit install        # 安装 pre-commit 钩子
$ poetry shell              # 激活虚拟环境
$ git commit                # 提交代码改动
# 正常情况，pre-commit 所配置的每个检查工具会开始依次执行...
```

## 代码协议
MIT LICENSE 为 bkpaas-python-sdk 的开源协议，你贡献的代码也会受此协议保护。